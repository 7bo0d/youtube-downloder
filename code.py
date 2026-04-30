from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from pytubefix import YouTube
import threading
import os

# -------- Global --------
Folder_Name = ""
choices = ["144p", "240p", "360p", "480p", "720p", "1080p", "🎵 Sound only"]


# -------- Functions --------
def openlocation():
    global Folder_Name
    Folder_Name = filedialog.askdirectory()
    if Folder_Name:
        locationError.config(text=Folder_Name, fg="#2ecc71")
        savePathVar.set(Folder_Name)
    else:
        locationError.config(text="No folder selected", fg="#e74c3c")


def start_download_thread():
    download_thread = threading.Thread(target=Downloadvideo)
    download_thread.daemon = True
    download_thread.start()


def update_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    progress_bar['value'] = percentage
    root.update_idletasks()


def Downloadvideo():
    global Folder_Name
    choice = ytdchoices.get()
    url = ytdEntry.get().strip()

    # Validations
    if not url:
        ytdError.config(text="❌ Please enter the link", fg="#e74c3c")
        return
    if "youtube.com" not in url and "youtu.be" not in url:
        ytdError.config(text="❌ Invalid YouTube link", fg="#e74c3c")
        return
    if not Folder_Name:
        ytdError.config(text="❌ Please select save path", fg="#e74c3c")
        return
    if not choice:
        ytdError.config(text="❌ Please choose quality", fg="#e74c3c")
        return

    ytdError.config(text="⏳ Connecting...", fg="#3498db")
    progress_bar['value'] = 0
    root.update()

    try:
        yt = YouTube(url, on_progress_callback=update_progress)
        select = None

        # Quality selection
        quality_map = {
            "144p": ("144p", True), "240p": ("240p", True), "360p": ("360p", True),
            "480p": ("480p", True), "720p": ("720p", True), "1080p": ("1080p", False)
        }
        if choice in quality_map:
            res, progressive = quality_map[choice]
            if progressive:
                select = yt.streams.filter(progressive=True, file_extension="mp4", res=res).first()
            else:
                select = yt.streams.filter(res=res).first()
        elif choice == "🎵 Sound only":
            select = yt.streams.filter(only_audio=True).order_by("abr").desc().first()

        if select is None:
            ytdError.config(text="⚠️ This quality is not available. Try another.", fg="#e67e22")
            progress_bar['value'] = 0
            return

        ytdError.config(text="📥 Downloading...", fg="#3498db")
        select.download(output_path=Folder_Name)
        ytdError.config(text="✅ Download completed!", fg="#2ecc71")

    except Exception as e:
        ytdError.config(text=f"❌ Error: {str(e)[:50]}", fg="#e74c3c")
        progress_bar['value'] = 0


# -------- UI Setup --------
root = Tk()
root.title("ABODY YouTube Downloader")
root.geometry("780x520")
root.resizable(False, False)
root.configure(bg="#f5f7fa")

# Center window
def center_window(window, w, h):
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    window.geometry(f'{w}x{h}+{x}+{y}')

center_window(root, 780, 520)

# Style
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TLabel", font=("Segoe UI", 10), background="#f5f7fa")
style.configure("TCombobox", font=("Segoe UI", 10))

# Header
header = Frame(root, bg="#2c3e50", height=70)
header.pack(fill=X)
title = Label(header, text="🎬 YouTube Downloader", font=("Segoe UI", 18, "bold"), fg="white", bg="#2c3e50")
title.pack(pady=15)

# Main content frame
main_frame = Frame(root, bg="#f5f7fa")
main_frame.pack(fill=BOTH, expand=True, padx=30, pady=20)

# URL Section
url_label = Label(main_frame, text="🔗 Video URL", font=("Segoe UI", 11, "bold"), bg="#f5f7fa", fg="#2c3e50")
url_label.grid(row=0, column=0, sticky=W, pady=(0,5))

ytdEntry = Entry(main_frame, width=70, font=("Segoe UI", 11), relief=FLAT, bd=1, highlightthickness=1, highlightcolor="#3498db")
ytdEntry.grid(row=1, column=0, columnspan=3, pady=(0,15), sticky=EW, ipady=8)

# Save path section
save_label = Label(main_frame, text="💾 Save Location", font=("Segoe UI", 11, "bold"), bg="#f5f7fa", fg="#2c3e50")
save_label.grid(row=2, column=0, sticky=W, pady=(0,5))

savePathVar = StringVar()
savePathEntry = Entry(main_frame, textvariable=savePathVar, width=50, font=("Segoe UI", 10), relief=FLAT, bd=1, state='readonly')
savePathEntry.grid(row=3, column=0, padx=(0,10), sticky=EW, ipady=6)

saveBtn = Button(main_frame, text="Browse", command=openlocation, font=("Segoe UI", 10, "bold"), bg="#3498db", fg="white", relief=FLAT, padx=15, pady=5, cursor="hand2")
saveBtn.grid(row=3, column=1, padx=(0,10))

locationError = Label(main_frame, text="No folder selected", font=("Segoe UI", 9), bg="#f5f7fa", fg="#e74c3c")
locationError.grid(row=3, column=2, sticky=W)

# Quality section
quality_label = Label(main_frame, text="🎞️ Quality", font=("Segoe UI", 11, "bold"), bg="#f5f7fa", fg="#2c3e50")
quality_label.grid(row=4, column=0, sticky=W, pady=(15,5))

ytdchoices = ttk.Combobox(main_frame, values=choices, state="readonly", font=("Segoe UI", 10), width=20)
ytdchoices.grid(row=5, column=0, sticky=W, pady=(0,20))

# Progress bar
progress_bar = ttk.Progressbar(main_frame, orient=HORIZONTAL, length=500, mode='determinate')
progress_bar.grid(row=6, column=0, columnspan=3, pady=(0,10), sticky=EW)

# Status label
ytdError = Label(main_frame, text="✨ Ready to download", font=("Segoe UI", 10), bg="#f5f7fa", fg="#7f8c8d")
ytdError.grid(row=7, column=0, columnspan=3, pady=(0,15))

# Download button
downloadBtn = Button(main_frame, text="⬇️ START DOWNLOAD", command=start_download_thread, font=("Segoe UI", 12, "bold"), bg="#2ecc71", fg="white", relief=FLAT, padx=25, pady=12, cursor="hand2")
downloadBtn.grid(row=8, column=0, columnspan=3, pady=10)

# Footer
footer = Label(root, text="Designed by ABDALLAH ALOBAIDY", font=("Segoe UI", 8), bg="#f5f7fa", fg="#bdc3c7")
footer.pack(side=BOTTOM, pady=10)

# Grid weights
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=0)
main_frame.columnconfigure(2, weight=0)

root.mainloop()