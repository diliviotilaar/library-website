from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime

# Inisialisasi aplikasi Flask.
app = Flask(__name__)

# Konfigurasi basis data MySQL untuk aplikasi.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/library_project'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = 'library_project'   # Konfigurasi kunci rahasia aplikasi.

# Membuat objek SQLAlchemy dengan menggunakan aplikasi Flask.
db = SQLAlchemy(app)

# Definisi model Buku untuk tabel 'buku' dalam basis data.
class Buku(db.Model):
    __tablename__ = 'buku'
    kode_buku = db.Column(db.String(10), primary_key=True)
    nama_buku = db.Column(db.String(100))
    kategori = db.Column(db.String(100))
    penulis = db.Column(db.String(100))
    penerbit = db.Column(db.String(100))
    sinopsis = db.Column(db.String(500))
    gambar = db.Column(db.String(100))

# Definisi model User untuk tabel 'user' dalam basis data.
class User(db.Model):
    __tablename__ = "user"
    id_mahasiswa = db.Column(db.String(10), primary_key=True)
    nama_mahasiswa = db.Column(db.String(100))
    password = db.Column(db.String(100))

# Definisi model Staff untuk tabel 'staff' dalam basis data.
class Staff(db.Model):
    __tablename__ = "staff"
    id_staff = db.Column(db.String(10), primary_key=True)
    nama_staff = db.Column(db.String(100))
    password = db.Column(db.String(100))

# Definisi model Peminjaman untuk tabel 'peminjaman_buku' dalam basis data.
class Peminjaman(db.Model):
    __tablename__ = "peminjaman_buku"
    id = db.Column(db.Integer, primary_key=True)
    id_mahasiswa = db.Column(db.String(10))
    kode_buku = db.Column(db.String(100))
    tanggal_peminjaman = db.Column(db.String(100))
    tanggal_pengembalian = db.Column(db.String(100))
    denda = db.Column(db.Integer)

def hitung_denda(tanggal1, tanggal2):
    # Menentukan format tanggal yang akan digunakan.
    format_tanggal = "%d-%m-%Y"
    try:
        # Mengubah string tanggal1 dan tanggal2 menjadi objek datetime sesuai dengan format yang ditentukan.
        tanggal1 = datetime.strptime(tanggal1, format_tanggal)
        tanggal2 = datetime.strptime(tanggal2, format_tanggal)
        
        # Menghitung selisih hari antara tanggal2 dan tanggal1.
        selisih = tanggal2 - tanggal1

        # Jika selisih dalam hari lebih dari 7 hari, menghitung denda berdasarkan selisih hari.
        if selisih.days > 7:
            denda = (selisih.days - 7)* 2000   # Denda 2.000 per 1 hari keterlambatan.
            return denda
        else:
            # Jika tidak ada keterlambatan lebih dari 7 hari, tidak ada denda.
            return None
   
    except ValueError:
        # Mengatasi kesalahan jika format tanggal tidak sesuai.
        return None

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/login', methods = ["POST", "GET"])
def login():
    if request.method == 'POST':
        # Jika permintaan adalah POST (mengirimkan data login), maka ambil data dari form.
        username = request.form["username"]
        password = request.form["password"]

        # Coba mencari pengguna (user) dan staf dengan username dan password yang cocok dalam basis data.
        found_user = User.query.filter_by(nama_mahasiswa = username, password = password).first()
        found_staff = Staff.query.filter_by(nama_staff = username, password = password).first()
        if found_user:
            # Jika pengguna ditemukan, simpan username dalam sesi dan arahkan ke halaman 'home'.
            session["username"] = username
            return redirect(url_for('home'))
        elif found_staff:
            # Jika staff ditemukan, simpan username dalam sesi dan arahkan ke halaman 'staff'.
            session["staff"] = username
            return redirect(url_for('staff'))
        else:
            # Jika tidak ada pengguna atau staf yang cocok, arahkan kembali ke halaman login.
            return render_template("index.html")
    else:
        # Jika permintaan adalah GET (tampilan halaman login), arahkan ke halaman login.
        return render_template("index.html")

@app.route('/home')
def home():
    if "username" in session:
        # Jika pengguna telah login, tampilkan halaman home.
        return render_template('home.html')
    else:
        # Jika tidak ada sesi pengguna yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))

@app.route('/staff')
def staff():
    if "staff" in session:
        # Jika staff telah login, tampilkan halaman staff.
        return render_template('staff.html')
    else:
        # Jika tidak ada sesi staff yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))

@app.route('/search', methods = ["POST", "GET"])
def search():
    if "username" in session:
        if request.method == 'POST':
            # Jika pengguna telah login dan permintaan adalah POST (mengirimkan pencarian), ambil data pencarian dari form.
            search = request.form["search"]

            # Cari buku dalam basis data yang cocok dengan pencarian yang diberikan.
            found_book = Buku.query.filter((
                                            Buku.nama_buku.ilike(f"%{search}%")|
                                            Buku.kategori.ilike(f"%{search}%")|
                                            Buku.penulis.ilike(f"%{search}%")|
                                            Buku.penerbit.ilike(f"%{search}%")|
                                            Buku.sinopsis.ilike(f"%{search}%")
                                            )).all()

            if found_book:
                # Jika buku ditemukan, tampilkan halaman 'books.html' dengan daftar buku yang cocok.
                return render_template('books.html', book_list = found_book )
            else:
                # Jika tidak ada buku yang cocok, kembalikan ke halaman 'home.html' dengan notifikasi bahwa tidak ada buku yang ditemukan.
                return render_template('home.html', not_found=True)
    else:
        # Jika pengguna belum login, arahkan kembali ke halaman login.
        return redirect(url_for("login"))
    
@app.route('/registration_page')
def registration_page():
    if "staff" in session:
        # Jika staff telah login, tampilkan halaman registrasi.
        return render_template('registration.html')
    else:
        # Jika tidak ada sesi staff yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))
    
@app.route('/registration', methods = ["POST", "GET"])
def registration():
    if "staff" in session:
        if request.method == 'POST':
            # Jika staf telah login dan permintaan adalah POST (pengiriman data registrasi), ambil data registrasi dari form.
            nama_mahasiswa = request.form["nama_mahasiswa"]
            password = request.form["password"]

            # Cek apakah pengguna dengan nama dan password tersebut sudah ada dalam basis data.
            found_user = User.query.filter_by(nama_mahasiswa = nama_mahasiswa, password = password).first()
            
            if found_user:
                # Jika pengguna sudah ada, arahkan kembali ke halaman registrasi.
                return redirect(url_for('registration_page'))
            else:
                # Jika pengguna belum ada, buat ID baru berdasarkan ID terakhir dalam basis data.
                latest_user_id = User.query.order_by(User.id_mahasiswa.desc()).first()
                latest_id = latest_user_id.id_mahasiswa
                new_id_number = str(int(latest_id[1:]) + 1)
                if len(new_id_number) == 1:
                    new_id = "m00" + str(new_id_number)
                elif len(new_id_number) == 2:
                    new_id = "m0" + str(new_id_number)
                elif len(new_id_number) == 3:
                    new_id = "m" + str(new_id_number)
                
                # Buat entri pengguna baru dan simpan dalam basis data.
                new_user = User(id_mahasiswa = new_id, nama_mahasiswa = nama_mahasiswa, password = password)
                db.session.add(new_user)
                # Simpan perubahan ke dalam basis data.
                db.session.commit()

                # Arahkan kembali ke halaman staff setelah pendaftaran berhasil.
                return redirect(url_for('staff'))
    else:
        # Jika tidak ada sesi staff yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))
        
@app.route('/borrow_page')
def borrow_page():
    if "staff" in session:
        # Jika staff telah login, tampilkan halaman peminjaman buku.
        return render_template('borrowing_book.html')
    else:
        # Jika tidak ada sesi staff yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))

@app.route('/borrow', methods = ["POST", "GET"])
def borrow():
    if "staff" in session:
        if request.method == 'POST':
            # Jika staff telah login dan permintaan adalah POST (pengiriman data peminjaman), ambil data peminjaman dari form.
            nama_mahasiswa = request.form["nama_mahasiswa"]
            nama_buku = request.form["nama_buku"]
            tanggal = request.form["tanggal"]
            
            # Cari pengguna dan buku dalam basis data.
            found_user = User.query.filter_by(nama_mahasiswa = nama_mahasiswa).first()
            found_book = Buku.query.filter_by(nama_buku = nama_buku).first()

            if found_book:
                kode_buku = found_book.kode_buku
                if found_user:
                    id = found_user.id_mahasiswa
                    # Buat entri peminjaman baru dan simpan dalam basis data.
                    new_data = Peminjaman(id_mahasiswa = id, kode_buku = kode_buku, tanggal_peminjaman = tanggal )
                    db.session.add(new_data)
                    # Simpan perubahan ke dalam basis data.
                    db.session.commit()

                    # Arahkan kembali ke halaman staff setelah peminjaman berhasil.
                    return redirect(url_for('staff'))
                else:
                    # Jika pengguna tidak ditemukan, tampilkan halaman peminjaman.
                    return render_template('borrowing_book.html')
            else:
                # Jika buku tidak ditemukan, tampilkan halaman peminjaman.
                return render_template('borrowing_book.html')
    else:
        # Jika tidak ada sesi staff yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))

@app.route('/return_book_page')
def return_book_page():
    if "staff" in session:
        # Jika staff telah login, tampilkan halaman pengembalian buku.
        return render_template('return_book.html')
    else:
        # Jika tidak ada sesi staff yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))

@app.route('/return_book', methods = ["POST", "GET"])
def return_book():
    if "staff" in session:
        if request.method == 'POST':
            # Jika staff telah login dan permintaan adalah POST (pengiriman data pengembalian), ambil data pengembalian dari form.
            nama_mahasiswa = request.form["nama_mahasiswa"]
            nama_buku = request.form["nama_buku"]
            tanggal = request.form["tanggal"]

            # Cari pengguna dan buku dalam basis data.
            found_user = User.query.filter_by(nama_mahasiswa = nama_mahasiswa).first()
            found_book = Buku.query.filter_by(nama_buku = nama_buku).first()

            if found_book:
                kode_buku = found_book.kode_buku
                if found_user:
                    id = found_user.id_mahasiswa
                    # Cari baris pada tabel peminjaman yang sesuai dengan pengguna dan buku.
                    row_to_update = Peminjaman.query.filter_by(id_mahasiswa = id, kode_buku = kode_buku).first()
                    if row_to_update:
                        # Update tanggal pengembalian.
                        row_to_update.tanggal_pengembalian = tanggal
                        tanggal_peminjaman = row_to_update.tanggal_peminjaman
                        # Hitung denda dan simpan ke dalam basis data.
                        fine = hitung_denda(tanggal_peminjaman, tanggal)
                        row_to_update.denda = fine
                        update_list = [nama_mahasiswa, nama_buku, tanggal_peminjaman, tanggal, fine]
                        # Simpan perubahan ke dalam basis data.
                        db.session.commit()

                        # Tampilkan halaman dengan informasi yang baru saja diperbaharui.
                        return render_template("fine.html", update_list = update_list)
                    else:
                        # Jika baris pada tabel peminjaman tidak ditemukan, arahkan kembali ke halaman pengembalian buku.
                        return redirect(url_for("return_book_page"))
                else:
                    # Jika pengguna tidak ditemukan, tampilkan halaman pengembalian buku.
                    return render_template('return_book.html')
            else:
                # Jika buku tidak ditemukan, tampilkan halaman pengembalian buku.
                return render_template('return_book.html')
    else:
        # Jika tidak ada sesi staff yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))

@app.route('/borrow_list')
def borrow_list():
    if "staff" in session:
        # Jika staff telah login, ambil daftar semua peminjaman buku dari basis data.
        borrow_list = Peminjaman.query.all()

        # Ambil tanggal hari ini dalam format yang sesuai.
        today = datetime.now()
        formated_date = today.strftime("%d-%m-%Y")

        # Iterasi melalui daftar peminjaman untuk menghitung denda jika buku belum dikembalikan.
        for borrow in borrow_list:
            if borrow.tanggal_pengembalian == None:
                borrow.denda = hitung_denda(borrow.tanggal_peminjaman, formated_date)
        # Simpan perubahan denda ke dalam basis data.
        db.session.commit()

        # Tampilkan halaman daftar peminjaman dengan informasi denda yang sudah diupdate.
        return render_template('borrow_list.html', borrow_list=borrow_list)
    else:
        # Jika tidak ada sesi staff yang aktif, arahkan kembali ke halaman login.
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    # Menghapus sesi pengguna yang aktif (logout) dan arahkan kembali ke halaman login.
    session.pop("username", None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)