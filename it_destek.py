import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# --- VERİTABANI --- #
def db_hazirla():
    conn = sqlite3.connect("it_destek_sistem.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS talepler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isim TEXT,
        bolum TEXT,
        sorun TEXT,
        durum TEXT
    )
    """)
    conn.commit()
    conn.close()

kullanici_pencereleri = {}

# --- TALEP EKLE --- #
def talep_ekle(isim, bolum, sorun):
    conn = sqlite3.connect("it_destek_sistem.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO talepler (isim, bolum, sorun, durum) VALUES (?, ?, ?, ?)",
                   (isim, bolum, sorun, "Beklemede"))
    conn.commit()
    talep_id = cursor.lastrowid
    conn.close()
    return talep_id

# --- TALEP PENCERESİ --- #
def talep_penceresi():
    pencere = tk.Toplevel(root)
    pencere.title("Destek Formu")
    pencere.configure(bg="#f0f8ff")

    tk.Label(pencere, text="Ad Soyad:", bg="#f0f8ff").pack()
    ent_isim = ttk.Entry(pencere); ent_isim.pack(pady=2)

    tk.Label(pencere, text="Bölüm:", bg="#f0f8ff").pack()
    ent_bolum = ttk.Entry(pencere); ent_bolum.pack(pady=2)

    tk.Label(pencere, text="Sorun:", bg="#f0f8ff").pack()
    txt_sorun = tk.Text(pencere, height=4, width=25, bg="#ffffe0")
    txt_sorun.pack(pady=2)

    def kaydet():
        isim = ent_isim.get()
        bolum = ent_bolum.get()
        sorun = txt_sorun.get("1.0", tk.END).strip()  # Düzeltilmiş

        if isim and bolum and sorun:
            talep_id = talep_ekle(isim, bolum, sorun)
            messagebox.showinfo("Başarılı", "Talep kaydedildi.")

            takip_pencere = tk.Toplevel(root)
            takip_pencere.title("{isim} Talep Takibi")
            takip_pencere.configure(bg="#e6f7ff")
            lbl = tk.Label(takip_pencere, text="Talebiniz: {sorun} Durum: Beklemede", bg="#e6f7ff")
            lbl.pack(padx=20, pady=20)

            kullanici_pencereleri[talep_id] = (takip_pencere, lbl)
            pencere.destroy()
        else:
            messagebox.showwarning("Hata", "Lütfen tüm alanları doldurun.")

    ttk.Button(pencere, text="Gönder", command=kaydet).pack(pady=5)

# --- ADMIN GİRİŞ --- #
def admin_giris():
    def giris_kontrol():
        if ent_sifre.get() == "1234":
            sifre_pencere.destroy()
            admin_penceresi()
        else:
            messagebox.showerror("Hata", "Şifre yanlış!")

    sifre_pencere = tk.Toplevel(root)
    sifre_pencere.title("Admin Girişi")
    sifre_pencere.configure(bg="#fff0f5")

    tk.Label(sifre_pencere, text="Şifre:", bg="#fff0f5").pack(pady=5)
    ent_sifre = ttk.Entry(sifre_pencere, show="*")
    ent_sifre.pack(pady=5)
    ttk.Button(sifre_pencere, text="Giriş Yap", command=giris_kontrol).pack(pady=5)

# --- ADMIN PANELİ --- #
def admin_penceresi():
    panel = tk.Toplevel(root)
    panel.title("Admin Paneli")
    panel.configure(bg="#f5f5dc")

    tablo = ttk.Treeview(panel, columns=("ID", "İsim", "Bölüm", "Sorun", "Durum"), show="headings")
    for baslik in ("ID", "İsim", "Bölüm", "Sorun", "Durum"):
        tablo.heading(baslik, text=baslik)
    tablo.pack(fill="both", expand=True, padx=5, pady=5)

    def listeyi_guncelle():
        for i in tablo.get_children(): tablo.delete(i)
        conn = sqlite3.connect("it_destek_sistem.db")
        for satir in conn.execute("SELECT * FROM talepler"):
            tablo.insert("", tk.END, values=satir)
        conn.close()

    def durumu_degistir():
        secili = tablo.selection()
        if secili:
            id_no, isim, bolum, sorun, _ = tablo.item(secili[0])['values']
            conn = sqlite3.connect("it_destek_sistem.db")
            conn.execute("UPDATE talepler SET durum='Çözüldü' WHERE id=?", (id_no,))
            conn.commit()
            conn.close()
            listeyi_guncelle()

            if id_no in kullanici_pencereleri:
                pencere, lbl = kullanici_pencereleri[id_no]
                lbl.config(text="Talebiniz: {sorun} Durum: Çözüldü")
                messagebox.showinfo("Bilgi", "{isim} adlı kullanıcı bilgilendirildi.")
            else:
                messagebox.showinfo("Bilgi", "{isim} adlı kullanıcının penceresi açık değil, bildirim gönderilemedi.")

    ttk.Button(panel, text="Çözüldü İşaretle", command=durumu_degistir).pack(side="left", padx=10)
    ttk.Button(panel, text="Listeyi Yenile", command=listeyi_guncelle).pack(side="left")
    listeyi_guncelle()

# --- ANA PROGRAM --- #
root = tk.Tk()
root.title("IT Destek Sistemi")
root.geometry("350x250")
root.configure(bg="#ffe4b5")  

tk.Label(root, text="IT Destek Sistemi", font=("Arial", 14, "bold"),
         bg="#ffe4b5", fg="#8b0000").pack(pady=20)

ttk.Button(root, text="Yeni Destek Talebi", width=25, command=talep_penceresi).pack(pady=5)
ttk.Button(root, text="Yönetici Paneli", width=25, command=admin_giris).pack(pady=5)

db_hazirla()
root.mainloop()