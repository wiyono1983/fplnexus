import streamlit as st
import pandas as pd
import os

FILE_EXCEL = "data_barang.xlsx"

st.set_page_config(page_title="POS Toko", page_icon="📦")

st.title("📦 POS Toko Sederhana")

# Buat file jika belum ada
if not os.path.exists(FILE_EXCEL):
    df_awal = pd.DataFrame(
        columns=[
            "Nama Barang",
            "Modal",
            "Margin (%)",
            "Harga Jual"
        ]
    )
    df_awal.to_excel(FILE_EXCEL, index=False)

# Baca data
df = pd.read_excel(FILE_EXCEL)

# Tambah barang
st.subheader("➕ Tambah Barang")

with st.form("form_barang"):

    nama_barang = st.text_input("Nama Barang")

    modal = st.number_input(
        "Harga Modal",
        min_value=0.0,
        step=100.0
    )

    margin = st.number_input(
        "Margin (%)",
        min_value=0,
        value=30
    )

    harga_jual = modal + (modal * margin / 100)

    st.info(
        f"Harga Jual Otomatis : Rp {harga_jual:,.0f}"
    )

    submit = st.form_submit_button("Simpan")

if submit:

    if nama_barang.strip() != "":

        data_baru = pd.DataFrame([
            {
                "Nama Barang": nama_barang,
                "Modal": modal,
                "Margin (%)": margin,
                "Harga Jual": round(harga_jual)
            }
        ])

        df = pd.concat(
            [df, data_baru],
            ignore_index=True
        )

        df.to_excel(FILE_EXCEL, index=False)

        st.success("Barang berhasil disimpan")
        st.rerun()

    else:
        st.warning("Nama barang wajib diisi")

# Tampilkan data
st.subheader("📋 Daftar Barang")

df = pd.read_excel(FILE_EXCEL)

st.dataframe(
    df,
    use_container_width=True
)

# Hapus barang
if len(df) > 0:

    st.subheader("🗑️ Hapus Barang")

    barang_hapus = st.selectbox(
        "Pilih Barang",
        df["Nama Barang"]
    )

    if st.button("Hapus"):

        df = df[
            df["Nama Barang"] != barang_hapus
        ]

        df.to_excel(
            FILE_EXCEL,
            index=False
        )

        st.success(
            f"{barang_hapus} berhasil dihapus"
        )

        st.rerun()

# Ringkasan
if len(df) > 0:

    st.subheader("📊 Ringkasan")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Jumlah Barang",
        len(df)
    )

    col2.metric(
        "Total Modal",
        f"Rp {df['Modal'].sum():,.0f}"
    )

    col3.metric(
        "Total Harga Jual",
        f"Rp {df['Harga Jual'].sum():,.0f}"
    )
