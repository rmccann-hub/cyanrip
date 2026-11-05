---
title: "Platterpus — Round 38 Drive Test"
subtitle: "Pioneer BDR-209D · Platterpus 0.7.121 · cyanrip .30"
date: "Printed copy of docs/rig-session.md, 5 November 2026"
---

# Platterpus — Round 38 Drive Test

**Drive:** Pioneer BDR-209D, firmware 1.51 · **Disc:** The Police, *Every Breath You Take: The Classics* (the reference disc)
**App:** Platterpus **0.7.121** · **Ripper:** cyanrip **.30** (`0.9.4-rc3+platterpus.30`, commit `5cc1c6b`)

> This is a printable copy of `docs/rig-session.md` in the Platterpus repository, which stays the master copy. If the two ever differ, the repository wins.

## What this test is for

Tracks 3 and 5 of the reference disc read differently from session to session on your drive. This test asks the drive itself why, from four angles:

1. **Does the drive have PureRead at all?** A read-only question to the drive, asked two ways.
2. **Does the session decide track 3?** The disc left in, against taken out, wiped and put back.
3. **Does the drive's own choice of speed decide track 3?** We fix the speed at 4x and 24x instead of letting the drive choose.
4. **Does a lower speed help track 5?** The fork asked for this.

The answers decide how round 38 closes. It also tests the new release 0.7.121, including the automatic CTDB repair.

## Ground rules

- **Every run is unattended.** It never stops to ask you anything. Touch the disc only **between** runs.
- **Nothing here changes the drive's firmware,** and nothing is burned. Do not update the drive's firmware during the test.
- **Never turn on Overread (`-O`)** on this drive. Nothing in this test does.
- **Write things down on the log sheet** (last pages) as you go: start and end times, every restart or shutdown, and anything unusual.
- **Send each phase's files to both sessions:** the Platterpus session and the cyanrip fork session.
- **Copy commands exactly.** Each grey box is one paste into the terminal.

## The plan at a glance

| Phase | Where | What you do | Your time | Machine time |
|---|---|---|---|---|
| 0 | Bazzite | Update Platterpus, choose `.30` | 10 min | — |
| 1, sitting 1 | Bazzite | Download, install tools, read the drive, start Run A | 10 min | 30–40 min (estimate) |
| 1, sitting 2 | Bazzite | Pack Run A, wipe the disc, paste one block (Run B, Run C, phase 2) | 5 min | 1 h 30 min – 2 h (estimate) |
| Send | Bazzite | Upload the files from phases 1 and 2 | 10 min | — |
| 3 | Windows 11, then Bazzite | Pioneer's utility, screenshots, PureRead to Perfect, Run D, put it back | about 1 h | 30–40 min |
| 4 | Bazzite | One Full acceptance run | 5 min | about 2 h 30 min |

*How the times are estimated:* none of these scripts has been timed yet. Track 3 is 4:51 and track 5 is 4:01 long, your drive reads them at about 2.8x to 3.1x, and each rip adds spin-up, a cache check and encoding, so about 2 to 3 minutes per rip. Run A and Run B are 12 rips each, and Run C is 17. Your runs will measure the real times.

---

# Phase 0 — Update Platterpus and choose `.30` (Bazzite, 10 minutes)

X **0.1** Open Platterpus.

X **0.2** **Tools → Setup & Updates… → Check for updates.** Take **0.7.121**. It restarts itself.

X **0.3** **Tools → Setup & Updates… → Choose a build…** Pick the one labelled as the **build under test**, `.30`.

X **0.4** **Help → About Platterpus…** Check two things:

- the version says **0.7.121**;
- the *Installed* line and the *Build under test* line show the **same commit** (`5cc1c6b`).

X **0.5** Close Platterpus.

**Log it:** write the time and "Phase 0 done, About shows 0.7.121 and .30" on the log sheet.
Phase 0 done, about shows 0.7.121 and .30
local time on PC 5:15 PM

---

# Phase 1 — Sitting 1 (Bazzite, about 10 minutes)

☐ **1.0** Put the reference disc in the drive. Open a terminal (Konsole). **Keep this terminal open** until sitting 2 is started.

## 1.1 Download the two test scripts and the read-only tools

☐ Paste:

```sh
BASE=https://raw.githubusercontent.com/the owner-hub/Platterpus/main/src/platterpus/rig_scripts
curl -L -o ~/drivemode.txt "$BASE/drivemode.txt"
curl -L -o ~/drivespeed.txt "$BASE/drivespeed.txt"
wc -c ~/drivemode.txt ~/drivespeed.txt
```

**Check:** the last line prints **8598** for `drivemode.txt` and **9492** for `drivespeed.txt`. If a number is tiny, the download failed; run it again.
This does show this, here is the output:
the owner@host:~ BASE=https://raw.githubusercontent.com/the owner-hub/Platterpus/main/src/platterpus/rig_scripts
curl -L -o ~/drivemode.txt "$BASE/drivemode.txt"
curl -L -o ~/drivespeed.txt "$BASE/drivespeed.txt"
wc -c ~/drivemode.txt ~/drivespeed.txt
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100   8598 100   8598   0      0  52071      0                              0
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100   9492 100   9492   0      0  87568      0                              0
 8598 ~/drivemode.txt
 9492 ~/drivespeed.txt
18090 total


X Paste (it may ask for your password, inside the container):

```sh
distrobox enter ripping -- sudo dnf install -y sg3_utils cdrdao
```

These tools only **read** from the drive.

the owner@host:~ distrobox enter ripping -- sudo dnf install -y sg3_utils cdrdao
Updating and loading repositories:
Repositories loaded.
Package                             Arch       Version                              Repository              Size
Installing:
 cdrdao                             x86_64     0:1.2.6-1.fc44                       updates              3.0 MiB
 sg3_utils                          x86_64     0:1.48-10.fc44                       updates              3.0 MiB
Installing dependencies:
 adwaita-cursor-theme               noarch     0:50.0-1.fc44                        fedora              11.4 MiB
 adwaita-icon-theme                 noarch     0:50.0-1.fc44                        fedora               1.1 MiB
 adwaita-icon-theme-legacy          noarch     0:46.2-7.fc44                        fedora               2.1 MiB
 alsa-lib                           x86_64     0:1.2.16.1-1.fc44                    updates              1.5 MiB
 at-spi2-atk                        x86_64     0:2.60.7-1.fc44                      updates            284.1 KiB
 at-spi2-core                       x86_64     0:2.60.7-1.fc44                      updates              1.6 MiB
 atk                                x86_64     0:2.60.7-1.fc44                      updates            252.5 KiB
 atkmm                              x86_64     0:2.28.5-1.fc44                      updates            373.7 KiB
 avahi-glib                         x86_64     0:0.9~rc2-8.fc44                     fedora              19.5 KiB
 cairomm                            x86_64     0:1.14.6-1.fc44                      updates            203.1 KiB
 colord-libs                        x86_64     0:1.4.8-4.fc44                       fedora             830.4 KiB
 cups-filesystem                    noarch     1:2.4.19-3.fc44                      updates              0.0   B
 cups-libs                          x86_64     1:2.4.19-3.fc44                      updates            634.6 KiB
 glib-networking                    x86_64     0:2.80.1-8.fc44                      updates            750.4 KiB
 glibmm2.4                          x86_64     0:2.66.10-1.fc44                     updates              2.9 MiB
 gsettings-desktop-schemas          x86_64     0:50.1-1.fc44                        updates              6.1 MiB
 gstreamer1                         x86_64     0:1.28.8-1.fc44                      updates              5.5 MiB
 gtk-update-icon-cache              x86_64     0:3.24.52-2.fc44                     updates             62.0 KiB
 gtk3                               x86_64     0:3.24.52-2.fc44                     updates             22.8 MiB
 gtkmm3.0                           x86_64     0:3.24.11-1.fc44                     updates              5.1 MiB
 hicolor-icon-theme                 noarch     0:0.18-3.fc44                        fedora              72.4 KiB
 json-glib                          x86_64     0:1.10.8-5.fc44                      fedora             596.2 KiB
 libXcomposite                      x86_64     0:0.4.6-7.fc44                       fedora              40.3 KiB
 libXcursor                         x86_64     0:1.2.3-4.fc44                       fedora              53.3 KiB
 libXdamage                         x86_64     0:1.1.6-7.fc44                       fedora              39.5 KiB
 libXi                              x86_64     0:1.8.3-1.fc44                       updates             80.6 KiB
 libXinerama                        x86_64     0:1.1.5-10.fc44                      fedora              14.8 KiB
 libXrandr                          x86_64     0:1.5.4-7.fc44                       fedora              55.6 KiB
 libXtst                            x86_64     0:1.2.5-4.fc44                       fedora              33.4 KiB
 libao                              x86_64     0:1.2.0-31.fc44                      fedora             127.9 KiB
 libcanberra                        x86_64     0:0.30-39.fc44                       fedora             265.6 KiB
 libcloudproviders                  x86_64     0:0.4.1-1.fc44                       updates            124.0 KiB
 libepoxy                           x86_64     0:1.5.10-12.fc44                     fedora               1.1 MiB
 libgusb                            x86_64     0:0.4.9-5.fc44                       fedora             157.9 KiB
 libmad                             x86_64     0:0.16.4-13.fc44                     fedora             179.0 KiB
 libsigc++20                        x86_64     0:2.12.2-1.fc44                      updates             92.6 KiB
 libsoup3                           x86_64     0:3.6.6-11.fc44                      updates              1.2 MiB
 libstemmer                         x86_64     0:3.0.1-11.fc44                      fedora             641.3 KiB
 libtinysparql                      x86_64     0:3.11.1-1.fc44                      updates              1.0 MiB
 libwayland-cursor                  x86_64     0:1.26.0-1.fc44                      updates             37.2 KiB
 libwayland-egl                     x86_64     0:1.26.0-1.fc44                      updates             12.3 KiB
 pangomm                            x86_64     0:2.46.4-5.fc44                      fedora             250.5 KiB
 sg3_utils-libs                     x86_64     0:1.48-10.fc44                       updates            309.4 KiB
 sound-theme-freedesktop            noarch     0:0.8-31.fc44                        fedora             460.4 KiB
 xprop                              x86_64     0:1.2.8-5.fc44                       fedora              54.5 KiB
Installing weak dependencies:
 adwaita-mono-fonts                 noarch     0:50.0-1.fc44                        fedora               5.6 MiB
 adwaita-sans-fonts                 noarch     0:50.0-1.fc44                        fedora               1.7 MiB
 dconf                              x86_64     0:0.49.0-5.fc44                      fedora             306.9 KiB
 libcanberra-gtk3                   x86_64     0:0.30-39.fc44                       fedora              70.4 KiB
 tinysparql                         x86_64     0:3.11.1-1.fc44                      updates              2.6 MiB

Transaction Summary:
 Installing:        52 packages

Total size of inbound packages is 23 MiB. Need to download 23 MiB.
After this operation, 86 MiB extra will be used (install 86 MiB, remove 0 B).
[ 1/52] sg3_utils-libs-0:1.48-10.fc44.x86_64                            100% | 493.5 KiB/s | 124.4 KiB |  00m00s
[ 2/52] sg3_utils-0:1.48-10.fc44.x86_64                                 100% |   3.1 MiB/s |   1.1 MiB |  00m00s
[ 3/52] cdrdao-0:1.2.6-1.fc44.x86_64                                    100% |   1.6 MiB/s | 764.4 KiB |  00m00s
[ 4/52] libao-0:1.2.0-31.fc44.x86_64                                    100% | 136.2 KiB/s |  53.8 KiB |  00m00s
[ 5/52] atkmm-0:2.28.5-1.fc44.x86_64                                    100% |   2.8 MiB/s |  95.3 KiB |  00m00s
[ 6/52] cairomm-0:1.14.6-1.fc44.x86_64                                  100% |   2.9 MiB/s |  62.4 KiB |  00m00s
[ 7/52] libmad-0:0.16.4-13.fc44.x86_64                                  100% | 219.2 KiB/s |  81.1 KiB |  00m00s
[ 8/52] pangomm-0:2.46.4-5.fc44.x86_64                                  100% | 241.3 KiB/s |  68.5 KiB |  00m00s
[ 9/52] adwaita-icon-theme-0:50.0-1.fc44.noarch                         100% |   3.2 MiB/s | 404.9 KiB |  00m00s
[10/52] colord-libs-0:1.4.8-4.fc44.x86_64                               100% |   4.3 MiB/s | 233.7 KiB |  00m00s
[11/52] glibmm2.4-0:2.66.10-1.fc44.x86_64                               100% |   2.8 MiB/s | 690.1 KiB |  00m00s
[12/52] hicolor-icon-theme-0:0.18-3.fc44.noarch                         100% |   1.7 MiB/s |  66.0 KiB |  00m00s
[13/52] libXcomposite-0:0.4.6-7.fc44.x86_64                             100% | 690.9 KiB/s |  24.2 KiB |  00m00s
[14/52] libXcursor-0:1.2.3-4.fc44.x86_64                                100% |   1.0 MiB/s |  32.5 KiB |  00m00s
[15/52] libXdamage-0:1.1.6-7.fc44.x86_64                                100% | 750.8 KiB/s |  23.3 KiB |  00m00s
[16/52] libXinerama-0:1.1.5-10.fc44.x86_64                              100% | 493.3 KiB/s |  14.3 KiB |  00m00s
[17/52] libXrandr-0:1.5.4-7.fc44.x86_64                                 100% | 926.9 KiB/s |  27.8 KiB |  00m00s
[18/52] libepoxy-0:1.5.10-12.fc44.x86_64                                100% |   4.0 MiB/s | 230.4 KiB |  00m00s
[19/52] adwaita-cursor-theme-0:50.0-1.fc44.noarch                       100% |   1.9 MiB/s | 380.7 KiB |  00m00s
[20/52] libgusb-0:0.4.9-5.fc44.x86_64                                   100% | 365.7 KiB/s |  64.7 KiB |  00m00s
[21/52] adwaita-icon-theme-legacy-0:46.2-7.fc44.noarch                  100% |   6.3 MiB/s |   2.5 MiB |  00m00s
[22/52] json-glib-0:1.10.8-5.fc44.x86_64                                100% |   2.3 MiB/s | 175.5 KiB |  00m00s
[23/52] libsigc++20-0:2.12.2-1.fc44.x86_64                              100% |   1.2 MiB/s |  39.5 KiB |  00m00s
[24/52] atk-0:2.60.7-1.fc44.x86_64                                      100% | 297.5 KiB/s |  82.4 KiB |  00m00s
[25/52] at-spi2-core-0:2.60.7-1.fc44.x86_64                             100% |   3.4 MiB/s | 402.1 KiB |  00m00s
[26/52] gtkmm3.0-0:3.24.11-1.fc44.x86_64                                100% |   2.2 MiB/s |   1.0 MiB |  00m00s
[27/52] libXtst-0:1.2.5-4.fc44.x86_64                                   100% | 678.1 KiB/s |  21.0 KiB |  00m00s
[28/52] xprop-0:1.2.8-5.fc44.x86_64                                     100% |   1.0 MiB/s |  35.3 KiB |  00m00s
[29/52] at-spi2-atk-0:2.60.7-1.fc44.x86_64                              100% |   2.0 MiB/s |  89.6 KiB |  00m00s
[30/52] libXi-0:1.8.3-1.fc44.x86_64                                     100% |   1.1 MiB/s |  41.3 KiB |  00m00s
[31/52] alsa-lib-0:1.2.16.1-1.fc44.x86_64                               100% |   2.0 MiB/s | 565.7 KiB |  00m00s
[32/52] gtk3-0:3.24.52-2.fc44.x86_64                                    100% |   3.9 MiB/s |   6.1 MiB |  00m02s
[33/52] cups-filesystem-1:2.4.19-3.fc44.noarch                          100% | 535.5 KiB/s |  12.3 KiB |  00m00s
[34/52] gtk-update-icon-cache-0:3.24.52-2.fc44.x86_64                   100% |   1.7 MiB/s |  33.8 KiB |  00m00s
[35/52] libtinysparql-0:3.11.1-1.fc44.x86_64                            100% |   5.8 MiB/s | 364.3 KiB |  00m00s
[36/52] libcloudproviders-0:0.4.1-1.fc44.x86_64                         100% | 623.8 KiB/s |  46.2 KiB |  00m00s
[37/52] avahi-glib-0:0.9~rc2-8.fc44.x86_64                              100% | 512.7 KiB/s |  15.4 KiB |  00m00s
[38/52] libwayland-cursor-0:1.26.0-1.fc44.x86_64                        100% | 801.6 KiB/s |  19.2 KiB |  00m00s
[39/52] libstemmer-0:3.0.1-11.fc44.x86_64                               100% |   2.6 MiB/s | 146.2 KiB |  00m00s
[40/52] cups-libs-1:2.4.19-3.fc44.x86_64                                100% | 631.4 KiB/s | 270.2 KiB |  00m00s
[41/52] libwayland-egl-0:1.26.0-1.fc44.x86_64                           100% | 539.7 KiB/s |  12.4 KiB |  00m00s
[42/52] libsoup3-0:3.6.6-11.fc44.x86_64                                 100% |   2.6 MiB/s | 409.5 KiB |  00m00s
[43/52] libcanberra-gtk3-0:0.30-39.fc44.x86_64                          100% | 951.9 KiB/s |  30.5 KiB |  00m00s
[44/52] libcanberra-0:0.30-39.fc44.x86_64                               100% |   2.2 MiB/s |  88.0 KiB |  00m00s
[45/52] glib-networking-0:2.80.1-8.fc44.x86_64                          100% | 936.0 KiB/s | 202.2 KiB |  00m00s
[46/52] gsettings-desktop-schemas-0:50.1-1.fc44.x86_64                  100% |   3.7 MiB/s | 864.4 KiB |  00m00s
[47/52] dconf-0:0.49.0-5.fc44.x86_64                                    100% |   2.1 MiB/s | 113.3 KiB |  00m00s
[48/52] sound-theme-freedesktop-0:0.8-31.fc44.noarch                    100% |   4.9 MiB/s | 382.5 KiB |  00m00s
[49/52] adwaita-sans-fonts-0:50.0-1.fc44.noarch                         100% |   4.0 MiB/s | 764.9 KiB |  00m00s
[50/52] adwaita-mono-fonts-0:50.0-1.fc44.noarch                         100% |   4.0 MiB/s |   1.4 MiB |  00m00s
[51/52] tinysparql-0:3.11.1-1.fc44.x86_64                               100% |   2.1 MiB/s |   1.0 MiB |  00m00s
[52/52] gstreamer1-0:1.28.8-1.fc44.x86_64                               100% |   4.4 MiB/s |   1.7 MiB |  00m00s
----------------------------------------------------------------------------------------------------------------
[52/52] Total                                                           100% |   6.1 MiB/s |  23.3 MiB |  00m04s
Running transaction
[ 1/54] Verify package files                                            100% | 742.0   B/s |  52.0   B |  00m00s
[ 2/54] Prepare transaction                                             100% | 675.0   B/s |  52.0   B |  00m00s
[ 3/54] Installing libsigc++20-0:2.12.2-1.fc44.x86_64                   100% |   9.2 MiB/s |  94.2 KiB |  00m00s
[ 4/54] Installing glibmm2.4-0:2.66.10-1.fc44.x86_64                    100% | 240.2 MiB/s |   2.9 MiB |  00m00s
[ 5/54] Installing cairomm-0:1.14.6-1.fc44.x86_64                       100% |  49.9 MiB/s | 204.3 KiB |  00m00s
[ 6/54] Installing libXi-0:1.8.3-1.fc44.x86_64                          100% |  26.6 MiB/s |  81.6 KiB |  00m00s
[ 7/54] Installing json-glib-0:1.10.8-5.fc44.x86_64                     100% |  24.8 MiB/s | 608.3 KiB |  00m00s
[ 8/54] Installing pangomm-0:2.46.4-5.fc44.x86_64                       100% |  49.2 MiB/s | 252.1 KiB |  00m00s
[ 9/54] Installing avahi-glib-0:0.9~rc2-8.fc44.x86_64                   100% |   9.9 MiB/s |  20.3 KiB |  00m00s
[10/54] Installing alsa-lib-0:1.2.16.1-1.fc44.x86_64                    100% |  50.3 MiB/s |   1.5 MiB |  00m00s
[11/54] Installing libao-0:1.2.0-31.fc44.x86_64                         100% |  18.3 MiB/s | 131.2 KiB |  00m00s
[12/54] Installing libgusb-0:0.4.9-5.fc44.x86_64                        100% |  31.2 MiB/s | 159.6 KiB |  00m00s
[13/54] Installing colord-libs-0:1.4.8-4.fc44.x86_64                    100% | 101.7 MiB/s | 833.4 KiB |  00m00s
[14/54] Installing libXtst-0:1.2.5-4.fc44.x86_64                        100% |  11.2 MiB/s |  34.5 KiB |  00m00s
[15/54] Installing gstreamer1-0:1.28.8-1.fc44.x86_64                    100% | 105.2 MiB/s |   5.5 MiB |  00m00s
[16/54] Installing sound-theme-freedesktop-0:0.8-31.fc44.noarch         100% |  20.7 MiB/s | 467.2 KiB |  00m00s
[17/54] Installing libcanberra-0:0.30-39.fc44.x86_64                    100% |   4.6 MiB/s | 270.5 KiB |  00m00s
[18/54] Installing gsettings-desktop-schemas-0:50.1-1.fc44.x86_64       100% | 180.3 MiB/s |   6.1 MiB |  00m00s
[19/54] Installing glib-networking-0:2.80.1-8.fc44.x86_64               100% |  29.9 MiB/s | 765.3 KiB |  00m00s
[20/54] Installing libsoup3-0:3.6.6-11.fc44.x86_64                      100% |  49.6 MiB/s |   1.2 MiB |  00m00s
[21/54] Installing libwayland-egl-0:1.26.0-1.fc44.x86_64                100% |   4.4 MiB/s |  13.4 KiB |  00m00s
[22/54] Installing libwayland-cursor-0:1.26.0-1.fc44.x86_64             100% |  12.5 MiB/s |  38.3 KiB |  00m00s
[23/54] Installing libstemmer-0:3.0.1-11.fc44.x86_64                    100% | 156.9 MiB/s | 642.7 KiB |  00m00s
[24/54] Installing libtinysparql-0:3.11.1-1.fc44.x86_64                 100% | 125.9 MiB/s |   1.0 MiB |  00m00s
[25/54] Installing libcloudproviders-0:0.4.1-1.fc44.x86_64              100% |  24.6 MiB/s | 125.9 KiB |  00m00s
[26/54] Installing gtk-update-icon-cache-0:3.24.52-2.fc44.x86_64        100% |   4.4 MiB/s |  63.2 KiB |  00m00s
[27/54] Installing cups-filesystem-1:2.4.19-3.fc44.noarch               100% | 593.8 KiB/s |   1.8 KiB |  00m00s
[28/54] Installing cups-libs-1:2.4.19-3.fc44.x86_64                     100% | 103.5 MiB/s | 636.2 KiB |  00m00s
[29/54] Installing xprop-0:1.2.8-5.fc44.x86_64                          100% |   3.9 MiB/s |  55.9 KiB |  00m00s
[30/54] Installing at-spi2-core-0:2.60.7-1.fc44.x86_64                  100% |  45.7 MiB/s |   1.6 MiB |  00m00s
[31/54] Installing atk-0:2.60.7-1.fc44.x86_64                           100% |  62.0 MiB/s | 253.9 KiB |  00m00s
[32/54] Installing atkmm-0:2.28.5-1.fc44.x86_64                         100% |  73.3 MiB/s | 375.2 KiB |  00m00s
[33/54] Installing at-spi2-atk-0:2.60.7-1.fc44.x86_64                   100% |  34.9 MiB/s | 286.2 KiB |  00m00s
[34/54] Installing adwaita-icon-theme-legacy-0:46.2-7.fc44.noarch       100% |  11.4 MiB/s |   2.4 MiB |  00m00s
[35/54] Installing adwaita-cursor-theme-0:50.0-1.fc44.noarch            100% | 476.2 MiB/s |  11.4 MiB |  00m00s
[36/54] Installing adwaita-icon-theme-0:50.0-1.fc44.noarch              100% |  14.3 MiB/s |   1.3 MiB |  00m00s
[37/54] Installing libepoxy-0:1.5.10-12.fc44.x86_64                     100% | 181.0 MiB/s |   1.1 MiB |  00m00s
[38/54] Installing libXrandr-0:1.5.4-7.fc44.x86_64                      100% |  18.5 MiB/s |  56.9 KiB |  00m00s
[39/54] Installing libXinerama-0:1.1.5-10.fc44.x86_64                   100% |   3.9 MiB/s |  15.9 KiB |  00m00s
[40/54] Installing libXdamage-0:1.1.6-7.fc44.x86_64                     100% |  13.4 MiB/s |  41.1 KiB |  00m00s
[41/54] Installing libXcursor-0:1.2.3-4.fc44.x86_64                     100% |  17.9 MiB/s |  55.0 KiB |  00m00s
[42/54] Installing libXcomposite-0:0.4.6-7.fc44.x86_64                  100% |  10.2 MiB/s |  41.9 KiB |  00m00s
[43/54] Installing hicolor-icon-theme-0:0.18-3.fc44.noarch              100% |   3.5 MiB/s | 179.7 KiB |  00m00s
[44/54] Installing gtk3-0:3.24.52-2.fc44.x86_64                         100% | 221.3 MiB/s |  22.8 MiB |  00m00s
[45/54] Installing gtkmm3.0-0:3.24.11-1.fc44.x86_64                     100% | 341.7 MiB/s |   5.1 MiB |  00m00s
[46/54] Installing libmad-0:0.16.4-13.fc44.x86_64                       100% |  44.2 MiB/s | 180.9 KiB |  00m00s
[47/54] Installing sg3_utils-libs-0:1.48-10.fc44.x86_64                 100% |  75.8 MiB/s | 310.7 KiB |  00m00s
[48/54] Installing sg3_utils-0:1.48-10.fc44.x86_64                      100% |  48.2 MiB/s |   3.0 MiB |  00m00s
[49/54] Installing cdrdao-0:1.2.6-1.fc44.x86_64                         100% | 116.5 MiB/s |   3.0 MiB |  00m00s
[50/54] Installing libcanberra-gtk3-0:0.30-39.fc44.x86_64               100% |   4.0 MiB/s |  73.7 KiB |  00m00s
[51/54] Installing tinysparql-0:3.11.1-1.fc44.x86_64                    100% |  44.3 MiB/s |   2.6 MiB |  00m00s
[52/54] Installing adwaita-sans-fonts-0:50.0-1.fc44.noarch              100% | 214.9 MiB/s |   1.7 MiB |  00m00s
[53/54] Installing adwaita-mono-fonts-0:50.0-1.fc44.noarch              100% | 372.9 MiB/s |   5.6 MiB |  00m00s
[54/54] Installing dconf-0:0.49.0-5.fc44.x86_64                         100% |  52.5 KiB/s | 311.5 KiB |  00m06s
Complete!


## 1.2 Ask the drive for its own settings (read-only)

x Paste:

```sh
mkdir -p ~/drivemode/dumps
dump() { distrobox enter ripping -- sh -c "date -u; $2" > ~/drivemode/dumps/$1.txt 2>&1; }
dump pioneer-f4 'sg_raw -R -r 256 /dev/sr0 3c 02 f4 00 00 00 00 01 00 00'
dump before 'sg_inq /dev/sr0; sg_get_config -q /dev/sr0; sg_get_config -q -H /dev/sr0; for c in 0 1 2 3; do echo "=== page control $c ==="; sg_modes -a -c $c /dev/sr0; done'
cat ~/drivemode/dumps/pioneer-f4.txt; wc -l ~/drivemode/dumps/before.txt
```

the owner@host:~ mkdir -p ~/drivemode/dumps
dump() { distrobox enter ripping -- sh -c "date -u; $2" > ~/drivemode/dumps/$1.txt 2>&1; }
dump pioneer-f4 'sg_raw -R -r 256 /dev/sr0 3c 02 f4 00 00 00 00 01 00 00'
dump before 'sg_inq /dev/sr0; sg_get_config -q /dev/sr0; sg_get_config -q -H /dev/sr0; for c in 0 1 2 3; do echo "=== page control $c ==="; sg_modes -a -c $c /dev/sr0; done'
the owner@host:~ mkdir -p ~/drivemode/dumps
dump() { distrobox enter ripping -- sh -c "date -u; $2" > ~/drivemode/dumps/$1.txt 2>&1; }
dump pioneer-f4 'sg_raw -R -r 256 /dev/sr0 3c 02 f4 00 00 00 00 01 00 00'
dump before 'sg_inq /dev/sr0; sg_get_config -q /dev/sr0; sg_get_config -q -H /dev/sr0; for c in 0 1 2 3; do echo "=== page control $c ==="; sg_modes -a -c $c /dev/sr0; done'
cat ~/drivemode/dumps/pioneer-f4.txt; wc -l ~/drivemode/dumps/before.txt
Thu Nov  5 10:20:26 PM UTC 2026
SCSI Status: Good 

Received 256 bytes of data:
 00     ff ff 02 02 ff ff ff 00  00 00 00 ff ff ff ff 00    ................
 10     00 ff ff 00 ff ff ff ff  ff ff ff ff 00 00 00 ff    ................
 20     ff ff ff ff ff ff ff 00  ff ff ff 00 00 00 00 00    ................
 30     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 40     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 50     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 60     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 70     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 80     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 90     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 a0     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 b0     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 c0     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 d0     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 e0     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
 f0     00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00    ................
289 ~/drivemode/dumps/before.txt
the owner@host:~ 


**What it does:** the first query is Pioneer's own settings read; the second lists the drive's standard settings pages and its feature list. Nothing is changed.

**Check:** `pioneer-f4.txt` shows rows of hex bytes, and `before.txt` is dozens of lines long.

- If `pioneer-f4.txt` says *illegal request*, also paste:
  `dump pioneer-f4-alt 'sg_raw -R -r 256 /dev/sr0 3c 01 f4 00 00 00 00 01 00 00'`
- If anything says *permission denied*, put `sudo ` in front of each command **inside** the quotes and paste again.

X Then ask the same question through the ripper itself (`.30`), as a second witness:

```sh
~/.local/bin/cyanrip -d /dev/sr0 -I -N -U --diagnostics ~/drivemode/dumps/cyanrip-vendor.json --read-vendor-settings > ~/drivemode/dumps/cyanrip-vendor.txt 2>&1
```

**What it does:** `.30` sends the same read-only query. Its answer should carry the same 256 bytes as `pioneer-f4.txt`, plus `.30`'s own reading of PureRead and everything else the drive says about itself.

**Log it:** the time, and anything an output said that looked like an error.
Ran this at 5:23 PM, finished in a few seconds, here is what it returned:
the owner@host:~ ~/.local/bin/cyanrip -d /dev/sr0 -I -N -U --diagnostics ~/drivemode/dumps/cyanrip-vendor.json --read-vendor-settings > ~/drivemode/dumps/cyanrip-vendor.txt 2>&1


## 1.3 Find your rips folder

X Paste:

```sh
RIPS="$(grep -E '^output_dir' ~/.config/platterpus/config.toml | sed -E 's/.*= *"(.*)"/\1/')"; RIPS="${RIPS:-$HOME/Music/rips}"; echo "$RIPS"
```

**Check:** it prints a folder path. Later steps use `$RIPS`. **In a new terminal, paste this line again first.**

## 1.4 Start Run A (disc left in)

X Close Platterpus if it is open. Paste:

```sh
~/Applications/platterpus-x86_64.AppImage --run-script ~/drivemode.txt
```

☐ **Leave it alone** until the app log says **DONE**: an estimated 30 to 40 minutes. Don't touch the disc.

**Log it:** the start time and the time it said DONE.

I think it ended early in error:
the owner@host:~ ~/Applications/platterpus-x86_64.AppImage --run-script ~/drivemode.txt
2026-11-05 17:24:30,846 INFO platterpus.app: platterpus 0.7.121 (build 2ca5196) starting; args: --run-script ~/drivemode.txt
2026-11-05 17:24:30,847 INFO platterpus.container_scope: removed INVOCATION_ID from our environment, so a container one of our tools starts gets its own scope instead of belonging to this window (podman keeps its monitor in the caller's unit while the variable is set)
2026-11-05 17:24:30,895 INFO platterpus.logging_setup: debug logging ENABLED
2026-11-05 17:24:31,006 INFO platterpus.app: Wayland session detected — preferring XWayland (QT_QPA_PLATFORM=xcb;wayland) to avoid the Plasma 6 black-window repaint bug; set QT_QPA_PLATFORM=wayland to force native Wayland.
2026-11-05 17:24:31,357 INFO platterpus.composition: using cyanrip backend (~/.local/bin/cyanrip)
2026-11-05 17:24:31,475 INFO platterpus.app: not arming the automatic cyanrip check — this launch runs a script
2026-11-05 17:24:31,562 INFO platterpus.ui.dialogs.centering: dialog presented: ScriptConsoleDialog ('Run test script') — the app now waits for the user
2026-11-05 17:24:31,563 INFO platterpus.app: --run-script ~/drivemode.txt -> found: ~/drivemode.txt
  (this is your copy, not the one packaged inside Platterpus at /tmp/.mount_plattebngFGE/opt/python3.14/lib/python3.14/site-packages/platterpus/rig_scripts/drivemode.txt — yours wins because it was found first; it is identical to it)
2026-11-05 17:24:31,564 INFO platterpus.app: unattended test script starting (--run-script)
2026-11-05 17:24:31,567 INFO platterpus.uiscript.runner: ui script run starting: 77 step(s)
2026-11-05 17:24:31,568 INFO platterpus.uiscript.runner: ui script Run estimate (full): about 47s: no rips, and the steps 47s (measured on the 2026-10-05 Full run, plus this script's waits).
2026-11-05 17:24:31,568 INFO platterpus.app: termination-signal handlers installed for [<Signals.SIGTERM: 15>, <Signals.SIGINT: 2>]
2026-11-05 17:24:31,574 INFO platterpus.ui.main_window: drive changed: /dev/sr0
2026-11-05 17:24:31,584 INFO platterpus.ui.main_window_provision: not making the first-run offers — this launch is running a script, so there is nobody to answer them
2026-11-05 17:24:31,825 INFO platterpus.deps.manager: dependency cyanrip build: the Platterpus fork (ok=True)
2026-11-05 17:24:34,185 INFO platterpus.ui.main_window: drive changed: /dev/sr0
2026-11-05 17:24:34,192 INFO platterpus.workers: worker thread DiscInfoWorker was superseded by a newer disc probe — abandoned while it finishes its current step (by design; reference retained, so process exit bypasses teardown until it finishes)
2026-11-05 17:26:31,928 WARNING platterpus.killable: ripper info probe: timed out after 120.0s; keeping the 109 character(s) it had already written — see the diagnostic record
2026-11-05 17:26:31,928 ERROR platterpus.diagnostics: platterpus-diagnostic [error] deps.command_failed: cyanrip timed out after 120s and was killed — it never reported an exit status
  tool: cyanrip
  exit code: none (no child was reaped)
  argv: ~/.local/bin/cyanrip -I -N -d /dev/sr0
  where: adapters.rip_backend.run_capture
  detail:
Checking /dev/sr0 for cdrom...
                CDROM sensed: PIONEER  BD-RW   BDR-209D 1.51 SCSI CD-ROM


Opening drive...
2026-11-05 17:26:31,928 INFO platterpus.workers.disc_info_worker: disc_info cancelled for /dev/sr0
2026-11-05 17:26:34,287 WARNING platterpus.killable: ripper info probe: timed out after 120.0s; keeping the 109 character(s) it had already written — see the diagnostic record
2026-11-05 17:26:34,287 ERROR platterpus.diagnostics: platterpus-diagnostic [error] deps.command_failed: cyanrip timed out after 120s and was killed — it never reported an exit status
  tool: cyanrip
  exit code: none (no child was reaped)
  argv: ~/.local/bin/cyanrip -I -N -d /dev/sr0
  where: adapters.rip_backend.run_capture
  detail:
Checking /dev/sr0 for cdrom...
                CDROM sensed: PIONEER  BD-RW   BDR-209D 1.51 SCSI CD-ROM


Opening drive...
2026-11-05 17:26:34,287 WARNING platterpus.workers.disc_info_worker: disc_info failed: cyanrip timed out after 120s
2026-11-05 17:26:34,287 INFO platterpus.ui.main_window_rip: freeing drive after scan (auto trigger), device=/dev/sr0
2026-11-05 17:26:34,288 INFO platterpus.ui.main_window_drive: disc read of /dev/sr0 failed; retrying automatically in 4000 ms (retry 1 of 2)
2026-11-05 17:26:34,309 WARNING platterpus.uiscript.runner: ui script L90 fail: rescan of /dev/sr0: the disc read had not finished after 120s, so later steps would act on a scan in flight
2026-11-05 17:26:34,410 INFO platterpus.drive_control: fuser -k (SIGKILL) /dev/sr0 rc=0
2026-11-05 17:26:34,410 INFO platterpus.drive_control: free_drive: killed=True
2026-11-05 17:26:38,294 INFO platterpus.ui.main_window_drive: automatic re-read 1 of 2 of /dev/sr0
2026-11-05 17:26:53,746 INFO platterpus.ui.main_window_picker: MusicBrainz returned 4 candidates for disc 'pNtImOkdBm9RMBIalzx0w9cfsYY-' — opening the release picker; the app will WAIT here until the user chooses (this is not a hang)
2026-11-05 17:26:53,756 INFO platterpus.ui.dialogs.centering: dialog presented: ReleasePickerDialog ('Pick a MusicBrainz release') — the app now waits for the user
2026-11-05 17:26:53,809 INFO platterpus.ui.dialogs.centering: dialog closed: ReleasePickerDialog ('Pick a MusicBrainz release') — accepted
2026-11-05 17:26:53,811 INFO platterpus.ui.main_window_picker: release picker: user chose 65282302-368b-4ba2-953a-483bcdef2410 after 0.1s
2026-11-05 17:26:57,434 INFO platterpus.uiscript.runner: ui script run ended: 1 step(s) have failed in 'B. drive offset, disc, and the time bound'; the first was L90 ('rescan': rescan of /dev/sr0: the disc read had not finished after 120s, so later steps would act on a scan in flight). no disc with five tracks is loaded — put the reference disc in, then run again
2026-11-05 17:26:57,436 INFO platterpus.uiscript.runner: ui script run saved to ~/.local/share/platterpus/uiscript/20261105T222431+0000
2026-11-05 17:26:57,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:26:58,820 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:26:59,790 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:00,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:01,830 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:02,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:03,820 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:04,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:05,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:06,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:07,790 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:08,821 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:09,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:10,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:11,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:12,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:13,819 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:14,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:15,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:16,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:17,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:18,820 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:19,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:20,790 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:21,790 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:22,789 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:23,819 INFO platterpus.app: unattended run: the batch is finished but its EVIDENCE BUNDLE is still being written — waiting. That archive is the file the operator sends; quitting now would truncate it.
2026-11-05 17:27:24,407 INFO platterpus.evidence_bundle: evidence bundle written: ~/.local/share/platterpus/bundles/platterpusbundle20261105t2224310000.tar.gz (10 file(s) in, 3 excluded, 4944278 bytes)
2026-11-05 17:27:24,413 INFO platterpus.uiscript.runner: SEND THIS ONE FILE: ~/.local/share/platterpus/bundles/platterpusbundle20261105t2224310000.tar.gz (10 file(s) in, 3 excluded; no audio)
2026-11-05 17:27:24,784 INFO platterpus.app: unattended run finished and post-rip work has settled — quitting. Nothing is left running, so the terminal will not ask.
2026-11-05 17:27:24,785 INFO platterpus.ui.dialogs.centering: dialog closed: ScriptConsoleDialog ('Run test script') — rejected or closed
2026-11-05 17:27:24,785 INFO platterpus.ui.main_window: window close requested (from the app itself); tearing down workers (rip active=False)
2026-11-05 17:27:24,931 INFO platterpus.exit_work: exit check: nothing holds /dev/sr0; no ripper process is running, as the host sees them — Platterpus left nothing behind
the owner@host:~ 


---

# Phase 1 — Sitting 2 (Bazzite, about 5 minutes, then unattended)

Do this when Run A says **DONE**.

☐ **1.5a** If this is a **new terminal**, first paste the `RIPS` line from step 1.3.

☐ **1.5b** Pack Run A. This moves its folders aside so Run B cannot overwrite them, and packs their logs, never audio:

```sh
mkdir -p ~/drivemode/runA && mv "$RIPS"/dm* ~/drivemode/runA/
tar czf ~/drivemode/runA-logs.tar.gz --exclude='*.flac' -C ~/drivemode runA
```

**Check:** no `cannot stat` error. If you see one, look at *If something goes wrong* at the end.

☐ **1.5c** Eject the disc. Wipe it gently **from the centre outward** with a soft, dry, lint-free cloth. Put it back and wait about **10 seconds**.

**Log it:** the time, what cloth you used, and whether you used any liquid (and which).

☐ **1.5d** Paste **this whole block** at once, then leave it. It runs Run B, then Run C (the speed test), then phase 2 (the track 9 reads), with no input from you:

```sh
APP=~/Applications/platterpus-x86_64.AppImage
"$APP" --run-script ~/drivemode.txt
mkdir -p ~/drivemode/runB && mv "$RIPS"/dm* ~/drivemode/runB/
tar czf ~/drivemode/runB-logs.tar.gz --exclude='*.flac' -C ~/drivemode runB
"$APP" --run-script ~/drivespeed.txt
mkdir -p ~/drivemode/runC && mv "$RIPS"/ds* ~/drivemode/runC/
tar czf ~/drivemode/runC-logs.tar.gz --exclude='*.flac' -C ~/drivemode runC
# phase 2: track 9 read two ways, then cdrdao
mkdir -p ~/drivemode/track9 && cd ~/drivemode/track9 && date -u > times.txt
flush() { distrobox enter ripping -- sh -c 'for l in 0 26 52 78 104 130 156 182 208 234 260 286; do sg_raw -R -r 61152 /dev/sr0 be 00 $(printf "%02x %02x %02x %02x" 0 0 $((l>>8)) $((l&255))) 00 00 1a 10 00 00 >/dev/null 2>&1; done'; }
for n in 1 2 3; do
  flush; { echo "raw$n"; distrobox enter ripping -- bash -c "time sg_raw -R -o raw$n.bin -r 39168 /dev/sr0 be 00 00 02 38 98 00 00 10 10 01 00"; } >> times.txt 2>&1
  flush; { echo "q$n"; distrobox enter ripping -- bash -c "time sg_raw -R -o q$n.bin -r 37888 /dev/sr0 be 00 00 02 38 98 00 00 10 10 02 00"; } >> times.txt 2>&1
done
ls -l *.bin >> times.txt
distrobox enter ripping -- cdrdao read-toc --device /dev/sr0 ~/drivemode/track9/cdrdao.toc > cdrdao-output.txt 2>&1
cd ~ && tar czf ~/drivemode/track9.tar.gz -C ~/drivemode track9
echo "Runs B and C and phase 2 done $(date -u)"
```

**Expected:** an estimated 1 h 30 min to 2 h. Overnight or during work is fine. It is finished when the terminal prints **Runs B and C and phase 2 done**.

**Normal, not a problem:** in Run C, if the drive refuses a set speed, those rips fail in seconds saying *"Device does not support changing speeds!"*. That is an answer, and the run carries on. Its last rip reads track 5 up to twelve times in one go.

**Log it:** the start time, and the time it printed *done*.

---

# Send the files from phases 1 and 2

☐ Upload these to **both** sessions (Platterpus and the cyanrip fork):

| File | Where it is |
|---|---|
| `pioneer-f4.txt` (and `pioneer-f4-alt.txt` if you made it) | `~/drivemode/dumps/` |
| `before.txt` | `~/drivemode/dumps/` |
| `cyanrip-vendor.json` and `cyanrip-vendor.txt` | `~/drivemode/dumps/` |
| `runA-logs.tar.gz`, `runB-logs.tar.gz`, `runC-logs.tar.gz` | `~/drivemode/` |
| `track9.tar.gz` | `~/drivemode/` |
| The three newest bundles | `~/.local/share/platterpus/bundles/` — `ls -t ~/.local/share/platterpus/bundles/ \| head -3` lists them |
| Your log sheet (a photo or the typed notes) | — |

☐ Add a line: anything unusual, such as a run that stopped early, or the room being very warm or cold.

---

# Phase 3 — Windows 11, then Bazzite (about an hour)

Do this when phases 1 and 2 are sent. It checks whether Pioneer's own utility works on your drive, and what PureRead does if it does.

## 3.1 Windows: look before changing anything

☐ **3.1a** Restart into **Windows 11**. **Log it:** the time, "restart".

☐ **3.1b** Download **`PioneerBDR-209-211_DriveUtility_v1.2.0.3.exe`** from Pioneer's page:
<https://pioneer.jp/device_e/product-e/ibs/device_e/dev00001r_e.html>
It is on the *Drive Utility* row for the BDR-209/211 series. Install it, choosing *Run as administrator* if it asks.

☐ **3.1c** Start it. **Whether it opens on your drive is itself an answer.** Pioneer lists it for the BDR-209EBK/UBK and 211, not the 209DBK.

- If it says **no supported drive**: screenshot that, and go to step **3.4**.

☐ **3.1d** If it opens, screenshot the **Pure Read** page **and** the **Advanced Quiet Drive** page **before changing anything**. Do **not** change Quiet Drive.

## 3.2 Windows: set PureRead to Perfect

☐ Choose **Perfect**, Apply, and screenshot it.

☐ **Restart** (not *Shut down*) straight into **Bazzite**, so the drive stays powered. **Log it:** the time, "restart".

## 3.3 Bazzite: read the settings again, then Run D

☐ **3.3a** Open a terminal. A restart forgets two things, so first paste these two lines again:

```sh
dump() { distrobox enter ripping -- sh -c "date -u; $2" > ~/drivemode/dumps/$1.txt 2>&1; }
RIPS="$(grep -E '^output_dir' ~/.config/platterpus/config.toml | sed -E 's/.*= *"(.*)"/\1/')"; RIPS="${RIPS:-$HOME/Music/rips}"; echo "$RIPS"
```

☐ **3.3b** Before any rip, read the drive again:

```sh
dump pioneer-f4-perfect 'sg_raw -R -r 256 /dev/sr0 3c 02 f4 00 00 00 00 01 00 00'
dump after-perfect 'sg_inq /dev/sr0; sg_get_config -q /dev/sr0; sg_get_config -q -H /dev/sr0; for c in 0 1 2 3; do echo "=== page control $c ==="; sg_modes -a -c $c /dev/sr0; done'
```

☐ **3.3c** Run D, with the disc left in:

```sh
~/Applications/platterpus-x86_64.AppImage --run-script ~/drivemode.txt
```

☐ **3.3d** When it says **DONE** (an estimated 30 to 40 minutes), pack it:

```sh
mkdir -p ~/drivemode/runD && mv "$RIPS"/dm* ~/drivemode/runD/
tar czf ~/drivemode/runD-logs.tar.gz --exclude='*.flac' -C ~/drivemode runD
```

## 3.4 Windows: put PureRead back

☐ **3.4a** Restart into Windows. Open the utility. Set Pure Read back to what your **first** screenshot showed. Apply. **Log it:** the times.

☐ **3.4b** Restart into Bazzite. Open a terminal, paste the `dump` line from 3.3a, then check it really went back:

```sh
dump pioneer-f4-restored 'sg_raw -R -r 256 /dev/sr0 3c 02 f4 00 00 00 00 01 00 00'
```

## Send the files from phase 3

☐ Upload to both sessions:

- every screenshot;
- `pioneer-f4-perfect.txt`, `after-perfect.txt` and `pioneer-f4-restored.txt` (in `~/drivemode/dumps/`);
- `runD-logs.tar.gz` and the newest bundle;
- your log sheet with the restarts.

If the utility did not open, the screenshot of what it said is all of phase 3.

---

# Phase 4 — One Full acceptance run (Bazzite, about 2 h 30 min)

This is the first real-hardware test of 0.7.121's automatic CTDB repair, and the Full run that tests the release.

☐ **4.1** Nothing to update: phase 0 already installed 0.7.121 and `.30`.

☐ **4.2** Open Platterpus. **Tools → Advanced → Run acceptance test…**, choose **Full**, and leave it. It holds sleep and the screen off, and puts your settings back at the end.

☐ **4.3** During the run, **don't close any other Platterpus window or any terminal you've used distrobox in.**

**Expect:** about 2 h 30 min (the last one took 2 h 31 min). Because repair is on by default, you may see `.before-ctdb-repair` files beside a repaired track, and remade MP3/WavPack/WAV copies. That is expected: the original is kept.

☐ **4.4** Upload the one `platterpusbundle….tar.gz` from the run's folder under `~/platterpus-rig/` to both sessions.

**Log it:** the start and end times.

---

# If something goes wrong

| What you see | What to do |
|---|---|
| `No such file or directory` for the AppImage | Paste `ls ~/Applications ~/Downloads \| grep -i platterpus`, and use the path it shows. |
| `mv: cannot stat …/dm*` (or `…/ds*`) | The rips went elsewhere. `find ~ -maxdepth 4 -type d -name 'dmfiveearly1'` (or `dsnospeed1`) shows where; use that folder instead of `$RIPS`. |
| A run stops before DONE | Send what it produced, with a note saying where it stopped. Don't restart it mid-run. |
| The app says fewer than five tracks | Take the disc out, put it back, wait 10 seconds, run again. |
| `sg_raw: command not found` | The install in step 1.1 didn't finish; paste it again. |
| `permission denied` from `sg_raw` or `sg_modes` | Put `sudo ` in front of each command **inside** the quotes and paste again. |
| `dump: command not found` | You're in a new terminal: paste the `dump` line from step 3.3a. |
| About doesn't show 0.7.121 and `.30` | Repeat phase 0 before running anything else. |

---

# Log sheet

Write times as you go. Your local time is fine; note **EST** beside it.

## Session details

| | |
|---|---|
| Date | |
| Disc in the drive (title) | |
| Room (normal / warm / cold) | |
| About shows 0.7.121 and `.30`? | ☐ yes ☐ no |

## Step times

| Step | Started | Finished | Notes |
|---|---|---|---|
| Phase 0, update and choose `.30` | | | |
| 1.2 drive readings | | | |
| 1.4 Run A | | | |
| 1.5c disc wiped (cloth, liquid?) | | | |
| 1.5d Run B, Run C, phase 2 | | | |
| Files from phases 1 and 2 sent | | | |
| 3.1 Windows utility opened? | | | ☐ opened ☐ "no supported drive" |
| 3.2 PureRead set to Perfect | | | |
| 3.3 Run D | | | |
| 3.4 PureRead put back | | | |
| Files from phase 3 sent | | | |
| Phase 4 Full run | | | |
| Phase 4 bundle sent | | | |

## Every restart, shutdown or power-off

Pioneer says a setting not stored in the drive is forgotten at power-off, so this list matters.

| Time | Restart or shutdown? | From → to (Bazzite / Windows) | Why |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

## Anything unusual

| Time | What happened |
|---|---|
| | |
| | |
| | |
| | |
