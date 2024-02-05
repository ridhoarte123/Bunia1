from tkinter import *
from tkinter import messagebox
import mysql.connector
from tkinter import ttk
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

class DataGuru(Tk):
    def __init__(self):
        super().__init__()
        self.title("Cuci Mobil")
        self.geometry("900x700")

        # Koneksi ke database
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cucimobil"
        )

        # Membuat kursor
        self.cursor = self.db.cursor()

        # Membuat dan menampilkan GUI
        self.tampilan_gui()

    def tampilan_gui(self):
        Label(self, text="Nomor Plat").grid(row=0, column=0, padx=10, pady=10)
        self.no_plat_entry = Entry(self, width=50)
        self.no_plat_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(self, text="Nama").grid(row=1, column=0, padx=10, pady=10)
        self.nama_entry = Entry(self, width=50)
        self.nama_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(self, text="Jenis Kendaraan").grid(row=2, column=0, padx=10, pady=10)
        self.jenis_kendaraan_entry = Entry(self, width=50)
        self.jenis_kendaraan_entry.grid(row=2, column=1, padx=10, pady=10)

        Label(self, text="Harga").grid(row=3, column=0, padx=10, pady=10)
        self.harga_entry = Entry(self, width=50)
        self.harga_entry.grid(row=3, column=1, padx=10, pady=10)

        Button(self, text="Simpan Data", command=self.simpan_data).grid(row=4, column=0, columnspan=2, pady=10)

        # Menambahkan Treeview
        self.tree = ttk.Treeview(self, columns=("no_plat", "nama", "jenis_kendaraan", "harga"), show="headings")
        self.tree.heading("no_plat", text="Plat Nomor")
        self.tree.heading("nama", text="Nama")
        self.tree.heading("jenis_kendaraan", text="jenis kendaraan")
        self.tree.heading("harga", text="Harga")
        self.tree.grid(row=5, column=0, columnspan=8, pady=10, padx=10)

        # Menambahkan tombol refresh data
        Button(self, text="Refresh Data", command=self.tampilkan_data).grid(row=4, column=1, columnspan=2, pady=10, padx=10)

        # Menambahkan tombol delete data
        Button(self, text="Delete Data", command=self.hapus_data).grid(row=6, column=1, columnspan=2, pady=10, padx=10)

        # Menambahkan tombol edit data
        Button(self, text="Edit Data", command=self.edit_data).grid(row=6, column=0, columnspan=2, pady=10, padx=10)

        #Menambahkan tombol print data
        Button(self, text="Print Data", command=self.cetak_ke_pdf).grid(row=6,column=3, columnspan=2, pady=10, padx=10)

        self.tampilkan_data()

    def simpan_data(self):
        no_plat = self.no_plat_entry.get()
        nama = self.nama_entry.get()
        jenis_kendaraan = self.jenis_kendaraan_entry.get()
        harga = self.harga_entry.get()

        query = "INSERT INTO data (no_plat, nama, jenis_kendaraan, harga) VALUES (%s, %s, %s, %s)"
        values = (no_plat, nama, jenis_kendaraan, harga)

        try:
            self.cursor.execute(query, values)
            self.db.commit()
            messagebox.showinfo("Sukses", "Data berhasil disimpan!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

        self.no_plat_entry.delete(0, END)
        self.nama_entry.delete(0, END)
        self.jenis_kendaraan_entry.delete(0, END)
        self.harga_entry.delete(0, END)

        self.tampilkan_data()

    def tampilkan_data(self):
        # Hapus data pada treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Ambil data dari database
        self.cursor.execute("SELECT * FROM data")
        data = self.cursor.fetchall()

        # Masukkan data ke treeview
        for row in data:
            self.tree.insert("", "end", values=row)

    def hapus_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang ingin dihapus.")
            return

        confirmation = messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus data terpilih?")
        if confirmation:
            for item in selected_item:
                data = self.tree.item(item, 'values')
                no_plat = data[0]
                query = "DELETE FROM data WHERE no_plat = %s"
                values = (no_plat,)

                try:
                    self.cursor.execute(query, values)
                    self.db.commit()
                    messagebox.showinfo("Sukses", "Data berhasil dihapus!")
                except Exception as e:
                    messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

            self.tampilkan_data()

    def edit_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih data yang ingin diedit.")
            return

        data = self.tree.item(selected_item[0], 'values')
        no_plat = data[0]

        # Retrieve existing data
        query = "SELECT * FROM data WHERE no_plat = %s"
        values = (no_plat,)

        try:
            self.cursor.execute(query, values)
            existing_data = self.cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
            return

        # Create a new window for editing
        edit_window = Toplevel(self)
        edit_window.title("Edit Data Cuci Mobil")

        Label(edit_window, text="Nama").grid(row=0, column=0, padx=10, pady=10)
        nama_entry = Entry(edit_window, width=50)
        nama_entry.grid(row=0, column=1, padx=10, pady=10)
        nama_entry.insert(0, existing_data[1])

        Label(edit_window, text="jenis Kendaraan").grid(row=1, column=0, padx=10, pady=10)
        jenis_kendaraan_entry = Entry(edit_window, width=50)
        jenis_kendaraan_entry.grid(row=1, column=1, padx=10, pady=10)
        jenis_kendaraan_entry.insert(0, existing_data[2])

        Label(edit_window, text="Harga").grid(row=2, column=0, padx=10, pady=10)
        harga_entry = Entry(edit_window, width=50)
        harga_entry.grid(row=2, column=1, padx=10, pady=10)
        harga_entry.insert(0, existing_data[3])

        Button(edit_window, text="Simpan Perubahan", command=lambda: self.simpan_perubahan(no_plat, nama_entry.get(), jenis_kendaraan_entry.get(), harga_entry.get(), edit_window)).grid(row=3, column=0, columnspan=2, pady=10)

    def simpan_perubahan(self, no_plat, nama, jenis_kendaraan, harga, edit_window):
        query = "UPDATE data SET nama=%s, jenis_kendaraan=%s, harga=%s WHERE no_plat=%s"
        values = (nama, jenis_kendaraan, harga, no_plat)

        try:
            self.cursor.execute(query, values)
            self.db.commit()
            messagebox.showinfo("Sukses", "Perubahan berhasil disimpan!")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")

        # Close the edit window
        edit_window.destroy()
        self.tampilkan_data()

    def cetak_ke_pdf(self):
        doc = SimpleDocTemplate("Data_cuci_mobil.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Membuat data untuk tabel PDF
        data = [["Nomor Plat", "Nama ", "Jenis Kendaraan", "harga"]]

        for row_id in self.tree.get_children():
            row_data = [self.tree.item(row_id, 'values')[0],
                        self.tree.item(row_id, 'values')[1],
                        self.tree.item(row_id, 'values')[2],
                        self.tree.item(row_id, 'values')[3]]

            data.append(row_data)
        # Membuat tabel PDF
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

        # Menambahkan tabel ke dokumen PDF
        doc.build([table])

        messagebox.showinfo("Sukses", "Data berhasil dicetak ke PDF(data_siswa.pdf).")

if __name__ == "__main__":
    app = DataGuru()
    app.mainloop()