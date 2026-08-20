# How to upload this to GitHub

You have two options. Option A (web) is easiest if you're new to git.

## Option A — Upload via GitHub website (no command line)

1. Go to https://github.com/new and create a new repository, e.g. `single-servo-dexterous-hand`. Leave it empty (don't add a README — you already have one).
2. On the new repo page, click **"uploading an existing file"**.
3. Drag the entire contents of this folder in (you can drag the folders too). Make sure the structure stays:
   ```
   README.md, LICENSE, requirements.txt, .gitignore
   src/  docs/  hardware/  media/
   ```
4. Write a commit message like `Initial commit` and click **Commit changes**.
5. Done — your README with the photo will render on the repo home page.

## Option B — Upload via git (command line)

From inside this folder:

```bash
git init
git add .
git commit -m "Initial commit: single-servo three-finger underactuated hand"
git branch -M main
git remote add origin https://github.com/<your-username>/single-servo-dexterous-hand.git
git push -u origin main
```

Replace `<your-username>` and the repo name with yours.

## Suggested repo settings

- **Description:** `A fully 3D-printable single-servo three-finger underactuated robotic hand.`
- **Topics (tags):** `robotics`, `gripper`, `dexterous-hand`, `underactuated`, `3d-printing`, `servo`, `python`
- Consider adding the assembled photo as the **social preview image** (Settings → Social preview).

## Before you publish — quick checklist

- [ ] Replace the placeholder in `src/servo_host.py` with your real servo driver (or note clearly that users must supply their own).
- [ ] Add your name/year to `LICENSE`.
- [ ] Optionally add the SolidWorks files: export each part as STL and the assembly as STEP, then put them in `hardware/cad/`. (STEP is an open format others can open without SolidWorks.)
- [ ] Add a short GIF or video of a grasp to `media/` and link it in the README — demos massively help a hardware repo.
