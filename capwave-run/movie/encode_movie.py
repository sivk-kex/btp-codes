from pathlib import Path

import av


source = Path("capwave.ppm")
target = Path("capwave.compat.mp4")

with av.open(source, format="image2pipe") as input_file:
    input_stream = input_file.streams.video[0]
    with av.open(target, "w", options={"movflags": "+faststart"}) as output_file:
        output_stream = output_file.add_stream(
            "libx264", rate=25,
            options={"profile": "baseline", "preset": "medium", "crf": "18"},
        )
        output_stream.width = 1024
        output_stream.height = 256
        output_stream.pix_fmt = "yuv420p"
        output_stream.codec_context.max_b_frames = 0

        for frame in input_file.decode(input_stream):
            frame = frame.reformat(width=1024, height=256, format="yuv420p")
            for packet in output_stream.encode(frame):
                output_file.mux(packet)

        for packet in output_stream.encode():
            output_file.mux(packet)
