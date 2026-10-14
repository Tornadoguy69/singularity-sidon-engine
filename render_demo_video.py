"""
Render a high-definition 60fps/30fps MP4 video of the 18,000-Particle
Singularity & Sidon engine using NumPy and ffmpeg.
Output is perfectly formatted for direct upload to Twitter (X).
"""

import os
import subprocess
import numpy as np

def generate_video(output_mp4="singularity_vortex_demo.mp4", width=1280, height=720, fps=30, duration_sec=8):
    total_frames = fps * duration_sec
    N = 18000
    
    # 1. Initialize particle geometries
    np.random.seed(42)
    radial_band = np.power(np.random.uniform(0, 1, N), 1.35) * 4.5 + 0.1
    angle0 = np.random.uniform(0, 2 * np.pi, N)
    z0 = (np.random.uniform(0, 1, N) - 0.5) * 8.0
    filament_id = (np.arange(N) % 48) / 48.0

    # Erdős Torus target coordinates
    u_torus = (np.arange(N) / N) * 2 * np.pi
    v_torus = ((np.arange(N) * 13) / N) * 2 * np.pi
    R_major = 3.2
    r_minor = 1.1

    pos_torus = np.zeros((N, 3))
    pos_torus[:, 0] = (R_major + r_minor * np.cos(v_torus)) * np.cos(u_torus)
    pos_torus[:, 1] = r_minor * np.sin(v_torus) * 1.2
    pos_torus[:, 2] = (R_major + r_minor * np.cos(v_torus)) * np.sin(u_torus)

    # Base colors
    colors = np.zeros((N, 3), dtype=np.float32)
    # Core proximity color: vermilion #FF4F00 for core, cyan #00F0FF for mid, violet for outer
    dist_r = radial_band
    mask_core = dist_r < 1.2
    mask_mid = (dist_r >= 1.2) & (dist_r < 3.0)
    mask_outer = dist_r >= 3.0

    colors[mask_core] = [255, 79, 0]     # Vermilion
    colors[mask_mid] = [0, 240, 255]     # Cyan
    colors[mask_outer] = [120, 110, 255] # Violet / Silver

    # Start ffmpeg process pipe
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "18",
        output_mp4
    ]

    pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    print(f"Rendering {total_frames} frames ({duration_sec}s @ {fps}fps) to {output_mp4}...")

    # Camera setup
    cam_dist = 11.5
    focal_length = 780.0

    for f in range(total_frames):
        tau = f / total_frames  # 0 to 1
        t_sec = f / fps

        # Mode transition: 0.0 -> 0.5 is Singularity Vortex collapse, 0.5 -> 1.0 is Torus Morph
        if tau < 0.5:
            # Vortex collapse mode
            morph = 0.0
            collapse = 0.15 + 0.82 * (tau / 0.5)
        else:
            # Morphing to Erdős Torus
            collapse = 0.97
            morph = (tau - 0.5) / 0.5
            morph = 0.5 - 0.5 * np.cos(morph * np.pi) # Smooth ease

        # 1. Compute vortex coordinates
        rem_t = max(1.0 - collapse, 0.008)
        lam = 0.588
        beta = 1.0 / (1.0 + lam)
        rad_scale = np.power(rem_t, beta)

        # Flow swirl
        swirl_rate = 1.8 + 2.5 * collapse
        theta = angle0 + t_sec * swirl_rate * (1.0 / (0.3 + radial_band * 0.4)) + filament_id * 6.28

        # Pinch neck
        pinch = 1.0 / (1.0 + 3.2 * np.exp(-z0 * z0 * 0.8) * collapse)
        r_dyn = radial_band * rad_scale * pinch
        z_dyn = z0 * (1.0 + 0.8 * collapse / (radial_band + 0.2))

        pos_vortex = np.zeros((N, 3))
        pos_vortex[:, 0] = r_dyn * np.cos(theta)
        pos_vortex[:, 1] = z_dyn * 0.75
        pos_vortex[:, 2] = r_dyn * np.sin(theta)

        # Interpolate with Torus
        pos_3d = pos_vortex * (1.0 - morph) + pos_torus * morph

        # Camera orbit
        cam_yaw = 0.4 + t_sec * 0.22
        cam_pitch = 0.35 + 0.12 * np.sin(t_sec * 0.4)

        # Rotate particles relative to camera
        cos_y, sin_y = np.cos(cam_yaw), np.sin(cam_yaw)
        cos_p, sin_p = np.cos(cam_pitch), np.sin(cam_pitch)

        # Yaw
        x1 = pos_3d[:, 0] * cos_y - pos_3d[:, 2] * sin_y
        z1 = pos_3d[:, 0] * sin_y + pos_3d[:, 2] * cos_y
        y1 = pos_3d[:, 1]

        # Pitch
        x2 = x1
        y2 = y1 * cos_p - z1 * sin_p
        z2 = y1 * sin_p + z1 * cos_p + cam_dist

        # Perspective projection
        inv_z = 1.0 / np.maximum(z2, 1.0)
        u = (x2 * inv_z * focal_length + width / 2.0).astype(np.int32)
        v = (-y2 * inv_z * focal_length + height / 2.0).astype(np.int32)

        # Blank obsidian canvas (#050507)
        frame = np.full((height, width, 3), [5, 5, 7], dtype=np.uint8)

        # Filter points in frustum
        valid = (u >= 1) & (u < width - 1) & (v >= 1) & (v < height - 1)
        u_v = u[valid]
        v_v = v[valid]
        c_v = colors[valid].astype(np.uint8)

        # Draw points with soft 2x2 splatting for luminous glow
        frame[v_v, u_v] = c_v
        frame[v_v + 1, u_v] = (c_v * 0.6).astype(np.uint8)
        frame[v_v, u_v + 1] = (c_v * 0.6).astype(np.uint8)

        # Add telemetry banner overlay on video
        pipe.stdin.write(frame.tobytes())

        if (f + 1) % 30 == 0:
            print(f"Rendered {f + 1}/{total_frames} frames...")

    pipe.stdin.close()
    pipe.wait()
    print(f"DONE! Video saved to: {output_mp4}")

if __name__ == "__main__":
    generate_video()
