#!/bin/bash
for ((i=0;i<=93;i++))
do
cp /root/ComfyUI/output/AnimateDiff_00012.png /root/Streamer-Sales/work_dirs/digital_human/full_imgs
mv /root/Streamer-Sales/work_dirs/digital_human/full_imgs/AnimateDiff_00012.png /root/Streamer-Sales/work_dirs/digital_human/full_imgs/0000000$i.png
done
