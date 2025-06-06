import threading
import tkinter
from tkinter import filedialog
import customtkinter
from yt_dlp import YoutubeDL

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

# Initialize global variables
download_path = ""
formats = []
is_downloading = False  # Flag to track if a download is in progress


def choose_download_location():
    global download_path
    download_path = filedialog.askdirectory(title="Select Download Folder")
    if download_path:
        location_label.configure(text=f"Download Folder: {download_path}")
    else:
        location_label.configure(text="No folder selected", text_color="red")


def fetch_formats():
    global formats
    try:
        yt_link = link.get()
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(yt_link, download=False)
            formats = info.get('formats', [])
            format_options = [f"{f['format_id']} - {f['ext']} - {f['resolution']}" for f in formats if 'resolution' in f]
            format_listbox.delete(0, tkinter.END)
            for option in format_options:
                format_listbox.insert(tkinter.END, option)
            format_label.configure(text="Select a format:")
    except Exception as e:
        format_label.configure(text=f"Error fetching formats: {str(e)}", text_color="red")


def download_video():
    global is_downloading
    if not download_path:
        finish_label.configure(text="Please select a download folder!", text_color="red")
        is_downloading = False
        download_btn.configure(state="normal")
        return

    selected_format_index = format_listbox.curselection()
    if not selected_format_index:
        finish_label.configure(text="Please select a format!", text_color="red")
        is_downloading = False
        download_btn.configure(state="normal")
        return

    selected_format = formats[selected_format_index[0]]['format_id']
    try:
        yt_link = link.get()
        ydl_opts = {
            'format': f'{selected_format}+bestaudio/best',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'progress_hooks': [on_progress_hook],
            # No postprocessors, to skip conversion
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_link])

        finish_label.configure(text="Download Complete!", text_color="green")
    except Exception as e:
        finish_label.configure(text=f"Error: {str(e)}", text_color="red")
    finally:
        is_downloading = False
        download_btn.configure(state="normal")


def start_download():
    global is_downloading
    if is_downloading:
        finish_label.configure(text="A download is already in progress!", text_color="red")
        return

    is_downloading = True
    download_btn.configure(state="disabled")  # Disable the button
    download_thread = threading.Thread(target=download_video)
    download_thread.start()


def on_progress_hook(d):
    if d['status'] == 'downloading':
        percentage = d['_percent_str'].strip()
        progress_label.configure(text=f"Progress: {percentage}")
        progress_bar.set(float(d['_percent_str'].strip('%')) / 100)
    elif d['status'] == 'finished':
        progress_label.configure(text="Merging files...")


# ProxyDown App
app = customtkinter.CTk()
app.geometry("600x600")
app.title("ProxyDown | A YouTube Video Downloader")

# Link Input
title_label = customtkinter.CTkLabel(app, text="Paste the video link:")
title_label.pack(padx=10, pady=10)

url_var = tkinter.StringVar()
link = customtkinter.CTkEntry(app, width=500, height=40, textvariable=url_var)
link.pack()

#fetch format button
fetch_formats_btn = customtkinter.CTkButton(app, text="Fetch Formats", command=fetch_formats)
fetch_formats_btn.pack(padx=10, pady=10)

#construct format space/list
format_label = customtkinter.CTkLabel(app, text="Available formats will appear here.")
format_label.pack()

format_listbox = tkinter.Listbox(app, width=70, height=10)
format_listbox.pack(padx=10, pady=10)

#button for download location
choose_folder_btn = customtkinter.CTkButton(app, text="Choose Download Folder", command=choose_download_location)
choose_folder_btn.pack(padx=10, pady=10)

location_label = customtkinter.CTkLabel(app, text="No folder selected", text_color="red")
location_label.pack()

#download button
download_btn = customtkinter.CTkButton(app, text="Download", command=start_download)
download_btn.pack(padx=10, pady=10)

#progress
progress_label = customtkinter.CTkLabel(app, text="Progress: 0%")
progress_label.pack()

progress_bar = customtkinter.CTkProgressBar(app, width=500)
progress_bar.set(0)
progress_bar.pack(padx=10, pady=10)

finish_label = customtkinter.CTkLabel(app, text="")
finish_label.pack()

app.mainloop()
