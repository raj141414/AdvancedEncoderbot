from bot_helper.Database.User_Data import get_data
from bot_helper.Others.Helper_Functions import get_video_duration
from bot_helper.Others.Names import Names
from os.path import isdir
from os import makedirs

def create_direc(direc):
    if not isdir(direc):
        makedirs(direc)
    return
    

def get_output_name(process_status):
    if process_status.file_name:
        return process_status.file_name
    else:
        return process_status.send_files[-1].split("/")[-1]


def get_commands(process_status):
    if process_status.process_type==Names.compress:
            compress_encoder = get_data()[process_status.user_id]['compress']['encoder']
            compress_preset = get_data()[process_status.user_id]['compress']['preset']
            compress_crf = get_data()[process_status.user_id]['compress']['crf']
            compress_map = get_data()[process_status.user_id]['compress']['map']
            compress_copysub = get_data()[process_status.user_id]['compress']['copy_sub']
            compress_sync = get_data()[process_status.user_id]['compress']['sync']
            create_direc(f"{process_status.dir}/compress/")
            log_file = f"{process_status.dir}/compress/compress_logs_{process_status.process_id}.txt"
            input_file = f'{str(process_status.send_files[-1])}'
            output_file = f"{process_status.dir}/compress/{get_output_name(process_status)}"
            file_duration = get_video_duration(input_file)
            command = ['ffmpeg','-hide_banner',
                                        '-progress', f"{log_file}",
                                        '-i', f'{input_file}']
            if compress_map:
                command+=['-map','0:v?',
                                            '-map',f'{str(process_status.amap_options)}?',
                                            "-map", "0:s?"]
            if compress_copysub:
                command+= ["-c:s", "copy"]
            if compress_encoder=='libx265':
                    command+= ['-vcodec','libx265','-vtag', 'hvc1']
            else:
                    command+= ['-vcodec','libx264']
            compress_use_queue_size = get_data()[process_status.user_id]['compress']['use_queue_size']
            if compress_use_queue_size:
                compress_queue_size = get_data()[process_status.user_id]['compress']['queue_size']
                command+= ['-max_muxing_queue_size', f'{str(compress_queue_size)}']
            if compress_sync:
                command+= ['-vsync', '1', '-async', '-1']
            command+= ['-preset', compress_preset, '-crf', f'{str(compress_crf)}', '-y', f"{output_file}"]
            return command, log_file, input_file, output_file, file_duration
    
    elif process_status.process_type==Names.watermark:
        watermark_position = get_data()[process_status.user_id]['watermark']['position']
        watermark_size = get_data()[process_status.user_id]['watermark']['size']
        watermark_encoder = get_data()[process_status.user_id]['watermark']['encoder']
        watermark_preset = get_data()[process_status.user_id]['watermark']['preset']
        watermark_crf = get_data()[process_status.user_id]['watermark']['crf']
        watermark_map = get_data()[process_status.user_id]['watermark']['map']
        watermark_copysub = get_data()[process_status.user_id]['watermark']['copy_sub']
        watermark_path = f'./userdata/{str(process_status.user_id)}_watermark.jpg'
        watermark_sync = get_data()[process_status.user_id]['watermark']['sync']
        create_direc(f"{process_status.dir}/watermark/")
        log_file = f"{process_status.dir}/watermark/watermark_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/watermark/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        command = ['ffmpeg','-hide_banner',
                                    '-progress', f"{log_file}",
                                    '-i', f'{str(input_file)}', "-i", f"{str(watermark_path)}"]
        if watermark_map:
            command+=['-map','0:v?',
                                        '-map',f'{str(process_status.amap_options)}?',
                                        "-map", "0:s?"]
        command+= ["-filter_complex", f"[1][0]scale2ref=w='iw*{watermark_size}/100':h='ow/mdar'[wm][vid];[vid][wm]overlay={watermark_position}"]
        if watermark_copysub:
            command+= ["-c:s", "copy"]
        if get_data()[process_status.user_id]['watermark']['encode']:
                if watermark_encoder=='libx265':
                        command+= ['-vcodec','libx265','-vtag', 'hvc1']
                else:
                        command+= ['-vcodec','libx264']
        else:
            command+= ['-codec:a','copy']
        watermark_use_queue_size = get_data()[process_status.user_id]['watermark']['use_queue_size']
        if watermark_use_queue_size:
            watermark_queue_size = get_data()[process_status.user_id]['watermark']['queue_size']
            command+= ['-max_muxing_queue_size', f'{str(watermark_queue_size)}']
        if watermark_sync:
                command+= ['-vsync', '1', '-async', '-1']
        command+= ['-preset', watermark_preset, '-crf', f'{str(watermark_crf)}', '-y', f'{str(output_file)}']
        return command, log_file, input_file, output_file, file_duration
    
    elif process_status.process_type==Names.merge:
            merge_map = get_data()[process_status.user_id]['merge']['map']
            merge_fix_blank = get_data()[process_status.user_id]['merge']['fix_blank']
            create_direc(f"{process_status.dir}/merge/")
            log_file = f"{process_status.dir}/merge/merge_logs_{process_status.process_id}.txt"
            infile_names = ""
            file_duration =0
            for dwfile_loc in process_status.send_files:
                infile_names += f"file '{str(dwfile_loc)}'\n"
                file_duration += get_video_duration(dwfile_loc)
            input_file = f"{process_status.dir}/merge/merge_files.txt"
            with open(input_file, "w", encoding="utf-8") as f:
                        f.write(str(infile_names).strip('\n'))
            output_file = f"{process_status.dir}/merge/{get_output_name(process_status)}"
            command = ['ffmpeg','-hide_banner',
                                    '-progress', f"{log_file}",
                                        "-f", "concat",
                                        "-safe", "0"]
            if merge_fix_blank:
                command += ['-segment_time_metadata', '1']
            command+=["-i", f'{str(input_file)}']
            if merge_fix_blank:
                command += ['-vf', 'select=concatdec_select', '-af', 'aselect=concatdec_select,aresample=async=1']
            if merge_map:
                command+=['-map','0']
            if not merge_fix_blank:
                command+= ["-c", "copy"]
            command+= ['-y', f'{str(output_file)}']
            return command, log_file, input_file, output_file, file_duration
        
    elif process_status.process_type==Names.softmux:
        softmux_preset =  get_data()[process_status.user_id]['softmux']['preset']
        softmux_crf = get_data()[process_status.user_id]['softmux']['crf']
        softmux_use_crf = get_data()[process_status.user_id]['softmux']['use_crf']
        softmux_encode = get_data()[process_status.user_id]['softmux']['encode']
        create_direc(f"{process_status.dir}/softmux/")
        log_file = f"{process_status.dir}/softmux/softmux_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/softmux/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        input_sub = []
        sub_map = []
        smap = 1
        for subtitle in process_status.subtitles:
            input_sub += ['-i', f'{str(subtitle)}']
            sub_map+= ['-map', f'{smap}:0']
            smap +=1
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}']
        command+= input_sub + sub_map + ['-map','0:v?', '-map',f'{str(process_status.amap_options)}?', '-map','0:s?', '-disposition:s:0','default']
        if softmux_encode:
                encoder = get_data()[process_status.user_id]['softmux']['encoder']
                if softmux_use_crf:
                        if encoder=='libx265':
                                command += ['-vcodec','libx265', '-vtag', 'hvc1', '-crf', f'{str(softmux_crf)}', '-preset', softmux_preset]
                        else:
                                command += ['-vcodec','libx264', '-crf', f'{str(softmux_crf)}', '-preset', softmux_preset]
                else:
                        if encoder=='libx265':
                                command += ['-vcodec','libx265', '-vtag', 'hvc1', '-preset', softmux_preset]
                        else:
                                command += ['-vcodec','libx264', '-preset', softmux_preset]
        else:
                command += ['-c','copy']
        command += ["-y", output_file]
        
        return command, log_file, input_file, output_file, file_duration
    
    elif process_status.process_type==Names.softremux:
        softremux_preset =  get_data()[process_status.user_id]['softremux']['preset']
        softremux_crf = get_data()[process_status.user_id]['softremux']['crf']
        softremux_use_crf = get_data()[process_status.user_id]['softremux']['use_crf']
        softremux_encode = get_data()[process_status.user_id]['softremux']['encode']
        create_direc(f"{process_status.dir}/softremux/")
        log_file = f"{process_status.dir}/softremux/softremux_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/softremux/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        input_sub = []
        sub_map = []
        smap = 1
        for subtitle in process_status.subtitles:
            input_sub += ['-i', f'{str(subtitle)}']
            sub_map+= ['-map', f'{smap}:0']
            smap +=1
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}']
        command+= input_sub + sub_map + ['-map','0:v?', '-map',f'{str(process_status.amap_options)}?', '-disposition:s:0','default']
        if softremux_encode:
                encoder = get_data()[process_status.user_id]['softremux']['encoder']
                if softremux_use_crf:
                        if encoder=='libx265':
                                command += ['-vcodec','libx265', '-vtag', 'hvc1', '-crf', f'{str(softremux_crf)}', '-preset', softremux_preset]
                        else:
                                command += ['-vcodec','libx264', '-crf', f'{str(softremux_crf)}', '-preset', softremux_preset]
                else:
                        if encoder=='libx265':
                                command += ['-vcodec','libx265', '-vtag', 'hvc1', '-preset', softremux_preset]
                        else:
                                command += ['-vcodec','libx264', '-preset', softremux_preset]
        else:
                command += ['-c','copy']
        command += ["-y", output_file]
        
        return command, log_file, input_file, output_file, file_duration