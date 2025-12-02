import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import os 
import shutil 
import random
from PIL import Image, ImageTk 

# ===============================================
# BAGIAN 1: DEFINISI CLASS FOTO (OBJECT)
# ===============================================

class Foto:
    """Blueprint for a Photo object (Model Data)."""
    def __init__(self, nama_file, path_lengkap, tags=[]):
        self.nama_file = nama_file
        self.path_lengkap = path_lengkap 
        self.tags = list(tags)

    def tambah_tag(self, tag_baru):
        """Method to add a tag to the photo."""
        tag_baru = tag_baru.strip().capitalize()
        if tag_baru and tag_baru not in self.tags:
            self.tags.append(tag_baru)
            self.tags.sort() 
            return True
        return False
    
    def hapus_tag(self, tag_yang_dihapus):
        """Method to remove a tag from the photo."""
        if tag_yang_dihapus in self.tags:
            self.tags.remove(tag_yang_dihapus)
            return True
        return False

    def get_info(self):
        """Returns basic information string (Tags are displayed separately)."""
        return (f"File: {self.nama_file}\n")
    
# ===============================================
# BAGIAN 2: DEFINISI CLASS PHOTOAPP (GUI APPLICATION & COLLECTION LOGIC)
# ===============================================

class PhotoApp:
    def __init__(self, master):
        self.master = master
        master.title("Photo Tagging System (Klasifikasi Foto)")
        master.geometry("1200x800") 

        self.koleksi_foto = []
        self.index_foto_saat_ini = 0
        self.foto_tk = None 
        
        self.kriteria_tag_list = set() 
        self.tag_unik_koleksi = set() 
        self.kelompok_tag_var = tk.StringVar(self.master)
        
        self.buat_layar_utama()
        self.buat_beranda()
        
        self.tampilkan_layar(self.frame_beranda)
        
        self.binding_keyboard()


    # --- Keyboard Binding Method (Shortcut) ---
    def binding_keyboard(self):
        self.master.bind("<Right>", lambda event: self.selanjutnya())
        self.master.bind("<Left>", lambda event: self.sebelumnya())


    # --- Screen Transition Method ---
    def tampilkan_layar(self, frame_yang_ditampilkan):
        for frame in [self.frame_beranda, self.frame_utama]:
            frame.pack_forget()
        
        frame_yang_ditampilkan.pack(fill=tk.BOTH, expand=True)

    # --- Home Screen ---
    def buat_beranda(self):
        self.frame_beranda = ttk.Frame(self.master, padding="50")
        
        ttk.Label(self.frame_beranda, text="SELAMAT DATANG DI PHOTO MANAGER", 
                  font=('Montserrat', 18, 'bold')).pack(pady=20)
        
        ttk.Label(self.frame_beranda, text="Silakan impor folder foto untuk memulai klasifikasi.", 
                  font=('Montserrat', 12)).pack(pady=10)
        
        ttk.Button(self.frame_beranda, 
                   text="🚀 IMPOR FOLDER FOTO", 
                   command=self.aksi_import_folder,
                   style='Accent.TButton' 
                   ).pack(pady=30, ipadx=20, ipady=10)
        
    # --- Function/Method to Create Main Screen GUI Elements (3 Columns) ---
    def buat_layar_utama(self):
        self.frame_utama = ttk.Frame(self.master)
        
        # 1. Control Frame (Left)
        self.frame_kontrol = ttk.Frame(self.frame_utama, padding="10", width=250)
        self.frame_kontrol.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.frame_kontrol.pack_propagate(False) 
        
        ttk.Button(self.frame_kontrol, 
                   text="← Kembali ke Import", 
                   command=lambda: self.tampilkan_layar(self.frame_beranda)
                   ).pack(fill=tk.X, pady=(0, 20))
        
        # --- PHOTO CONTROL ---
        ttk.Label(self.frame_kontrol, text="PHOTO CONTROL", font=('Montserrat', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # B. Add Tag Criteria
        ttk.Label(self.frame_kontrol, text="Tambah Tag Kriteria :", font=('Montserrat', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        self.tag_entry = ttk.Entry(self.frame_kontrol)
        self.tag_entry.pack(fill=tk.X, pady=2)
        self.tag_entry.bind("<Return>", lambda event: self.aksi_tambah_kriteria_tag())
        
        # C. Container to display added tag criteria (as buttons)
        ttk.Label(self.frame_kontrol, text="Tag Kriteria yang Tersedia:", font=('Montserrat', 10)).pack(anchor='w', pady=(10, 5))
        self.frame_tag_kriteria_list = ttk.Frame(self.frame_kontrol, padding=5, relief="groove", borderwidth=2)
        self.frame_tag_kriteria_list.pack(fill=tk.X, pady=5)
        
        # D. Navigation
        ttk.Separator(self.frame_kontrol, orient='horizontal').pack(fill=tk.X, pady=10)
        
        self.frame_navigasi = ttk.Frame(self.frame_kontrol)
        self.frame_navigasi.pack(fill=tk.X, pady=5)
        ttk.Button(self.frame_navigasi, text="<", command=self.sebelumnya, style='Big.TButton', width=5).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(self.frame_navigasi, text=">", command=self.selanjutnya, style='Big.TButton', width=5).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Label Status Foto (Contoh: 1/20)
        self.label_status = ttk.Label(self.frame_kontrol, text="0/0", font=('Arial', 10, 'bold'))
        self.label_status.pack(pady=(15, 5))


        # 2. Preview Frame (Center)
        self.frame_tengah = ttk.Frame(self.frame_utama, padding="10")
        self.frame_tengah.pack(side=tk.LEFT, expand=True, fill=tk.BOTH) 
        
        ttk.Label(self.frame_tengah, text="PHOTO REVIEW", font=('Montserrat', 14, 'bold')).pack(pady=5)
        
        # ## [FIX] Mengganti ttk.Label menjadi tk.Label agar width dan height berfungsi
        self.image_label = tk.Label(self.frame_tengah, 
                                     background="#eeeeee", 
                                     text="Image Preview Placeholder", 
                                     relief="sunken",
                                     width=100, 
                                     height=40) 
        self.image_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True) 


        # 3. Info Frame (Right)
        self.frame_info_kanan = ttk.Frame(self.frame_utama, padding="10", width=250) 
        self.frame_info_kanan.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        self.frame_info_kanan.pack_propagate(False) 

        # --- METADATA INFO ---
        ttk.Label(self.frame_info_kanan, text="METADATA INFO", font=('Montserrat', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.label_filename = ttk.Label(self.frame_info_kanan, text="File Name: -", wraplength=230)
        self.label_filename.pack(anchor='w', pady=1)

        ttk.Label(self.frame_info_kanan, text="Tags Applied:").pack(anchor='w', pady=(5, 1))

        self.frame_tag_metadata = ttk.Frame(self.frame_info_kanan)
        self.frame_tag_metadata.pack(fill=tk.X, pady=5)
        
        # --- PHOTO GROUP ---
        ttk.Separator(self.frame_info_kanan, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(self.frame_info_kanan, text="PHOTO GROUP", font=('Montserrat', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.kelompok_tag_var.set("Pilih Tag") 
        self.kelompok_tag_dropdown = ttk.OptionMenu(
            self.frame_info_kanan, 
            self.kelompok_tag_var, 
            "Pilih Tag", 
            "Pilih Tag" 
        )
        self.kelompok_tag_dropdown.pack(fill=tk.X, pady=2)
        
        ttk.Button(self.frame_info_kanan, 
                   text="EXPORT A COPY", 
                   style='Accent.TButton',
                   command=self.aksi_tombol_kelompokkan).pack(fill=tk.X, pady=10)

    # ===============================================
    # METHOD PEMELIHARAAN TAG UNIK GLOBAL
    # ===============================================

    def recalculate_unique_collection_tags(self):
        """Regenerates the set of all unique tags present across ALL photos in the collection."""
        new_unique_tags = set()
        for foto in self.koleksi_foto:
            for tag in foto.tags:
                new_unique_tags.add(tag)
        self.tag_unik_koleksi = new_unique_tags
        
    # --- File and Import Logic Method ---
    def aksi_import_folder(self):
        """Opens folder dialog and loads photos into the collection."""
        folder_path = filedialog.askdirectory(title="Pilih Folder Foto")
        if not folder_path:
            return

        self.koleksi_foto = [] 
        self.tag_unik_koleksi = set() 
        self.kriteria_tag_list = set() 
        
        foto_ditemukan = 0
        tipe_foto = ('.jpg', '.jpeg', '.png', '.gif', '.tif')

        try:
            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(tipe_foto):
                    full_path = os.path.join(folder_path, file_name)
                    
                    foto = Foto(file_name, full_path)
                    self.koleksi_foto.append(foto)
                    
                    for tag in foto.tags:
                        self.tag_unik_koleksi.add(tag)
                    
                    foto_ditemukan += 1

        except Exception as e:
             messagebox.showerror("Import Error", f"Terjadi kesalahan saat membaca folder: {e}")
             return

        if foto_ditemukan > 0:
            self.tampilkan_layar(self.frame_utama)
            self.index_foto_saat_ini = 0
            self.update_tag_kriteria_view() 
            self.update_dropdown_photo_group()
            self.tampilkan_foto_saat_ini()
            messagebox.showinfo("Import Success", f"🎉 {foto_ditemukan} foto berhasil diimpor.")
        else:
            messagebox.showwarning("Warning", "Tidak ada file foto (JPG/PNG/GIF/TIF) yang ditemukan.")
            self.tampilkan_layar(self.frame_beranda) 
            
        # Panggil update status setelah koleksi terisi (apapun hasilnya)
        self.update_status_display()


    # --- Tag Criteria Method (Left Control Panel) ---
    def aksi_tambah_kriteria_tag(self):
        """Adds a tag from the input to the criteria list, NOT to the photo."""
        tag_baru = self.tag_entry.get().strip().capitalize()
        
        if not tag_baru:
            messagebox.showwarning("Warning", "Nama Tag Kriteria tidak boleh kosong.")
            return

        if tag_baru not in self.kriteria_tag_list:
            self.kriteria_tag_list.add(tag_baru)
            self.update_tag_kriteria_view() 
            self.tag_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", f"Tag Kriteria '{tag_baru}' sudah ada.")

    def aksi_hapus_kriteria_tag(self, tag_kriteria):
        """Removes a tag from the available criteria list AND removes it from ALL photos."""
        
        konfirmasi = messagebox.askokcancel(
            "Konfirmasi Penghapusan", 
            f"Anda yakin ingin menghapus tag kriteria '{tag_kriteria}'? Tindakan ini akan menghapus tag ini dari daftar kriteria DAN SEMUA FOTO dalam koleksi."
        )

        if not konfirmasi:
            return 
            
        self.kriteria_tag_list.discard(tag_kriteria)
        self.update_tag_kriteria_view()
        
        is_current_photo_affected = False
        
        for i, foto in enumerate(self.koleksi_foto):
            if foto.hapus_tag(tag_kriteria):
                if i == self.index_foto_saat_ini:
                    is_current_photo_affected = True
                    
        self.tag_unik_koleksi.discard(tag_kriteria)
        self.update_dropdown_photo_group()

        if is_current_photo_affected:
            self.tampilkan_foto_saat_ini()
            
        messagebox.showinfo("Kriteria Dihapus", 
                            f"Tag Kriteria '{tag_kriteria}' berhasil dihapus dari daftar DAN SEMUA FOTO.")


    def update_tag_kriteria_view(self):
        """Recreates the tag criteria buttons in Photo Control."""
        for widget in self.frame_tag_kriteria_list.winfo_children():
            widget.destroy()
            
        if not self.kriteria_tag_list:
            ttk.Label(self.frame_tag_kriteria_list, text="Tambahkan tag di atas.").pack(anchor='w', padx=5, pady=5)
            return
            
        sorted_kriteria = sorted(list(self.kriteria_tag_list))
        
        for tag in sorted_kriteria:
            frame_tag = ttk.Frame(self.frame_tag_kriteria_list, relief="solid")
            frame_tag.pack(fill=tk.X, pady=2, padx=2)
            
            ttk.Button(frame_tag, 
                       text=tag, 
                       style='Tag.TButton', 
                       command=lambda t=tag: self.aksi_terapkan_tag(t)
                       ).pack(side=tk.LEFT, fill=tk.X, expand=True)
                           
            ttk.Button(frame_tag, 
                       text="X", 
                       width=3, 
                       style='Danger.TButton',
                       command=lambda t=tag: self.aksi_hapus_kriteria_tag(t)
                       ).pack(side=tk.RIGHT)
                           
    def aksi_terapkan_tag(self, tag_yang_diterapkan):
        """Applies a tag from the criteria to the current photo."""
        if not self.koleksi_foto: return

        foto_saat_ini = self.koleksi_foto[self.index_foto_saat_ini]
        
        if foto_saat_ini.tambah_tag(tag_yang_diterapkan):
            self.tag_unik_koleksi.add(tag_yang_diterapkan)
            self.update_dropdown_photo_group()
            self.tampilkan_foto_saat_ini() 
        else:
            messagebox.showwarning("Warning", f"Tag '{tag_yang_diterapkan}' sudah ada di foto ini.")
            
    # --- Grouping Logic Method ---
    def update_dropdown_photo_group(self):
        """Updates the option list in the Photo Group Dropdown based on the unique tag collection."""
        tag_list = sorted(list(self.tag_unik_koleksi))
        
        options = ["Pilih Tag"] + tag_list
        
        menu = self.kelompok_tag_dropdown["menu"]
        menu.delete(0, "end")
        
        for tag in options:
            menu.add_command(label=tag, command=tk._setit(self.kelompok_tag_var, tag))

        current_selection = self.kelompok_tag_var.get()
        if current_selection not in options:
            self.kelompok_tag_var.set("Pilih Tag")
        elif current_selection == "Pilih Tag" and len(options) > 1:
            pass


    def aksi_tombol_kelompokkan(self):
        kriteria = self.kelompok_tag_var.get().strip()
        if kriteria == "Pilih Tag":
             messagebox.showwarning("Warning", "Pilih tag yang valid dari dropdown.")
             return
        self.aksi_pindahkan_file(kriteria)

    def aksi_pindahkan_file(self, kriteria_tag):
        """Menyalin file dengan kriteria tag ke folder baru yang dipilih pengguna."""
        if kriteria_tag == "Pilih Tag":
            return

        lokasi_dasar = filedialog.askdirectory(title=f"Pilih Folder Tujuan untuk Tag: {kriteria_tag}")
        
        if not lokasi_dasar:
            messagebox.showwarning("Dibatalkan", "Operasi penyalinan dibatalkan oleh pengguna.")
            return

        safe_tag = "".join(c for c in kriteria_tag if c.isalnum() or c in (' ', '_')).rstrip()
        nama_folder_tag = f"KOLEKSI_{safe_tag.upper().replace(' ', '_')}"
        folder_output = os.path.join(lokasi_dasar, nama_folder_tag)
        
        if not os.path.exists(folder_output):
            try:
                os.makedirs(folder_output)
            except Exception as e:
                messagebox.showerror("Folder Error", f"Gagal membuat folder di lokasi yang dipilih: {e}")
                return
            
        foto_disalin = 0
        tag_kapital = kriteria_tag.strip().capitalize()
        
        for foto in self.koleksi_foto: 
            if tag_kapital in foto.tags:
                try:
                    tujuan_path = os.path.join(folder_output, foto.nama_file)
                    shutil.copy2(foto.path_lengkap, tujuan_path) 
                    foto_disalin += 1
                except Exception as e:
                    print(f"Failed to copy {foto.nama_file}: {e}")
                    
        if foto_disalin > 0:
            messagebox.showinfo("Grouping Complete", 
                                 f"✅ {foto_disalin} foto dengan tag '{kriteria_tag}' berhasil dikelompokkan (disalin) ke:\n{folder_output}")
        else:
            messagebox.showwarning("Not Found", f"Tidak ada foto dengan tag '{kriteria_tag}' yang ditemukan.")

    # Method untuk memperbarui status display (Contoh: 1/20)
    def update_status_display(self):
        total_foto = len(self.koleksi_foto)
        
        if total_foto > 0:
            # Indeks dimulai dari 0, jadi kita tambahkan 1 untuk tampilan pengguna
            index_saat_ini = self.index_foto_saat_ini + 1 
            status_text = f"{index_saat_ini}/{total_foto}"
        else:
            status_text = "0/0"
            
        self.label_status.config(text=status_text)
            
    # --- Navigation & Display Control Method ---    
    def tampilkan_foto_saat_ini(self):
        """Loads the image, resizes it, and displays the info."""
        if not self.koleksi_foto:
            return

        foto_saat_ini = self.koleksi_foto[self.index_foto_saat_ini]
        
        # --- A. Display Metadata (Text Info) ---
        self.label_filename.config(text=f"File Name: {foto_saat_ini.nama_file}")
        self.perbarui_tampilan_tag_metadata(foto_saat_ini)


        # --- B. Display Image (Pillow Logic) ---
        try:
            img_pil = Image.open(foto_saat_ini.path_lengkap)
                        
            self.frame_tengah.update_idletasks() 
            
            CONTAINER_PADDING = 40
            
            max_width = self.frame_tengah.winfo_width() - CONTAINER_PADDING
            max_height = self.frame_tengah.winfo_height() - CONTAINER_PADDING 
            
            
            if max_width < 100 or max_height < 100:
                max_width = 640 
                max_height = 700 
                
                if self.master.winfo_width() > 100:
                     max_width = self.master.winfo_width() - 500 
                     max_height = self.master.winfo_height() - 100 


            lebar_asli, tinggi_asli = img_pil.size
            rasio_lebar = max_width / lebar_asli
            rasio_tinggi = max_height / tinggi_asli
            rasio = min(rasio_lebar, rasio_tinggi)
            
            if rasio > 1:
                rasio = 1

            lebar_baru = int(lebar_asli * rasio)
            tinggi_baru = int(tinggi_asli * rasio)
            
            img_pil = img_pil.resize((lebar_baru, tinggi_baru), Image.LANCZOS)
            
            self.foto_tk = ImageTk.PhotoImage(img_pil)
            self.image_label.config(image=self.foto_tk, text="")
            
        except Exception as e:
            self.image_label.config(image='', text=f"Gagal memuat gambar: {e}", background="#ffdddd")
            
        # Panggil update status setiap foto ditampilkan
        self.update_status_display()
            
    def perbarui_tampilan_tag_metadata(self, foto):
        """Removes and recreates the applied Tag display in Metadata Info (Right Panel)."""
        
        for widget in self.frame_tag_metadata.winfo_children():
            widget.destroy()
            
        if not foto.tags:
            ttk.Label(self.frame_tag_metadata, text="- Belum ada tag -").pack(anchor='w', padx=5)
            return

        for tag in foto.tags:
            frame_tag = ttk.Frame(self.frame_tag_metadata, borderwidth=1, relief="solid", style='TagInfo.TFrame')
            frame_tag.pack(fill=tk.X, pady=2, padx=2)
            
            ttk.Label(frame_tag, text=tag, padding=3).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            ttk.Button(frame_tag, 
                       text="X", 
                       width=3, 
                       style='Danger.TButton',
                       command=lambda t=tag: self.aksi_hapus_tag_foto(t)
                       ).pack(side=tk.RIGHT)

    def aksi_hapus_tag_foto(self, tag_yang_dihapus):
        
        if not self.koleksi_foto: return

        foto_saat_ini = self.koleksi_foto[self.index_foto_saat_ini]
        if foto_saat_ini.hapus_tag(tag_yang_dihapus):
            self.recalculate_unique_collection_tags()
            self.update_dropdown_photo_group()
            self.tampilkan_foto_saat_ini()
            
    def sebelumnya(self):
        if self.index_foto_saat_ini > 0:
            self.index_foto_saat_ini -= 1
            self.tampilkan_foto_saat_ini()
        else:
            messagebox.showinfo("Navigasi", "Ini adalah foto pertama.")

    def selanjutnya(self):
        if self.index_foto_saat_ini < len(self.koleksi_foto) - 1:
            self.index_foto_saat_ini += 1
            self.tampilkan_foto_saat_ini()
        else:
            messagebox.showinfo("Navigasi", "Ini adalah foto terakhir.")
            
# ===============================================
# BAGIAN 3: EKSEKUSI PROGRAM
# ===============================================

if __name__ == "__main__":
    root = tk.Tk()
    
    # Style Configuration
    style = ttk.Style(root)
    if 'clam' in style.theme_names():
        style.theme_use('clam')
        
    # --- Color Palette ---
    COLOR_ACCENT = '#4a86e8'
    COLOR_DANGER = '#dc3545'
    COLOR_TAG_BG = '#e6e6e6'
        
    # Main Button Style (Blue)
    style.configure('Accent.TButton', font=('Montserrat', 14, 'bold'), foreground='white', background=COLOR_ACCENT)
    style.map('Accent.TButton', background=[('active', '#3c78d8')])
    
    # Danger Button Style (Red)
    style.configure('Danger.TButton', font=('Montserrat', 8, 'bold'), foreground='white', background=COLOR_DANGER, borderwidth=0)
    style.map('Danger.TButton', background=[('active', '#c82333')])
    
    # Large Navigation Button Style
    style.configure('Big.TButton', font=('Montserrat', 16, 'bold'))
    
    # Tag Criteria Button Style (Clickable tags on the left)
    style.configure('Tag.TButton', font=('Montserrat', 10), background=COLOR_TAG_BG, foreground='#333333', borderwidth=0)
    style.map('Tag.TButton', background=[('active', '#cccccc')])

    # Tag Info Frame Style (For tags displayed on the right metadata panel)
    style.configure('TagInfo.TFrame', background=COLOR_TAG_BG, relief="flat", borderwidth=0)

    # Make the default window background white/light grey for contrast
    root.configure(background="#f5f5f5")
    
    app = PhotoApp(root)
    root.mainloop()
