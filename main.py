import streamlit as st
import pandas as pd
import time
import json
import yaml
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import asyncio
import threading
from pathlib import Path

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="NetPilot - Network Automation Suite",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    
    .stMetric > div {
        color: white !important;
    }
    
    .device-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    
    .task-button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
    }
    
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    
    .log-container {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'devices' not in st.session_state:
    st.session_state.devices = [
        {'name': 'arista-sw-001', 'ip': '172.20.20.101', 'type': 'Arista EOS', 'status': 'Online'},
        {'name': 'arista-sw-002', 'ip': '172.20.20.102', 'type': 'Arista EOS', 'status': 'Online'},
        {'name': 'cisco-sw-001', 'ip': '10.10.10.11', 'type': 'Cisco IOS', 'status': 'Offline'},
        {'name': 'cisco-sw-002', 'ip': '10.10.10.12', 'type': 'Cisco IOS', 'status': 'Online'}
    ]

if 'logs' not in st.session_state:
    st.session_state.logs = [
        f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] NetPilot automation suite initialized",
        f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Loaded {len(st.session_state.devices)} devices from inventory",
        f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Connection pool ready with 10 threads",
        f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] cisco-sw-001: Connection timeout",
        f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Ready for automation tasks..."
    ]

if 'task_running' not in st.session_state:
    st.session_state.task_running = False

def add_log(message, log_type="INFO"):
    """Log mesajı ekle"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{log_type}] {message}"
    st.session_state.logs.append(log_entry)
    # Son 50 log'u tut
    if len(st.session_state.logs) > 50:
        st.session_state.logs = st.session_state.logs[-50:]

def get_device_stats():
    """Cihaz istatistiklerini hesapla"""
    total = len(st.session_state.devices)
    online = sum(1 for device in st.session_state.devices if device['status'] == 'Online')
    offline = total - online
    return total, online, offline

def run_automation_task(task_type):
    """Otomasyon görevini çalıştır"""
    if st.session_state.task_running:
        st.error("Bir görev zaten çalışıyor!")
        return
    
    st.session_state.task_running = True
    
    task_messages = {
        'config': [
            'Starting configuration deployment...',
            'Connecting to arista-sw-001...',
            'Configuration applied successfully on arista-sw-001',
            'Connecting to arista-sw-002...',
            'Configuration applied successfully on arista-sw-002',
            'Failed to connect to cisco-sw-001',
            'Configuration deployment completed'
        ],
        'backup': [
            'Starting backup process...',
            'Backing up arista-sw-001...',
            'Backup saved: output/arista-sw-001_backup.cfg',
            'Backing up arista-sw-002...',
            'Backup saved: output/arista-sw-002_backup.cfg',
            'Backup process completed'
        ],
        'inventory': [
            'Starting inventory collection...',
            'Collecting from arista-sw-001...',
            'Collecting from arista-sw-002...',
            'Inventory saved: output/network_inventory.json',
            'Inventory collection completed'
        ],
        'firmware': [
            'Starting firmware update process...',
            'This operation may take several minutes...',
            'Uploading firmware to devices...',
            'Firmware update completed successfully'
        ]
    }
    
    messages = task_messages.get(task_type, ['Unknown task executed'])
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, message in enumerate(messages):
        progress = (i + 1) / len(messages)
        progress_bar.progress(progress)
        status_text.text(f"İşlem durumu: {message}")
        
        # Log ekle
        if 'Failed' in message:
            add_log(message, "ERROR")
        elif 'may take' in message:
            add_log(message, "WARN")
        else:
            add_log(message, "INFO")
        
        time.sleep(0.8)  # Gerçek zamanlı his için
    
    st.session_state.task_running = False
    st.success(f"{task_type.title()} görevi başarıyla tamamlandı!")
    time.sleep(1)
    st.rerun()

# Ana başlık
st.title("🌐 NetPilot - Network Automation Suite")
st.markdown("**Multi-Vendor Network Management Platform**")

# Sidebar - Kontrol Paneli
with st.sidebar:
    st.header("🛠️ Kontrol Paneli")
    
    # Görev Butonları
    st.subheader("Otomasyon Görevleri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Config Deploy", disabled=st.session_state.task_running, use_container_width=True):
            run_automation_task('config')
        
        if st.button("📊 Inventory", disabled=st.session_state.task_running, use_container_width=True):
            run_automation_task('inventory')
    
    with col2:
        if st.button("💾 Backup", disabled=st.session_state.task_running, use_container_width=True):
            run_automation_task('backup')
        
        if st.button("🔄 Firmware", disabled=st.session_state.task_running, use_container_width=True):
            run_automation_task('firmware')
    
    st.divider()
    
    # Dosya Yükleme
    st.subheader("📁 Dosya Yükleme")
    uploaded_file = st.file_uploader(
        "Device Inventory",
        type=['csv', 'yaml', 'yml'],
        help="CSV veya YAML formatında cihaz envanteri yükleyin"
    )
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ {uploaded_file.name} yüklendi")
            add_log(f"File uploaded: {uploaded_file.name}")
        elif uploaded_file.name.endswith(('.yaml', '.yml')):
            content = yaml.safe_load(uploaded_file)
            st.success(f"✅ {uploaded_file.name} yüklendi")
            add_log(f"YAML file processed: {uploaded_file.name}")
    
    st.divider()
    
    # Ayarlar
    st.subheader("⚙️ Ayarlar")
    thread_count = st.slider("Thread Sayısı", 1, 20, 10)
    timeout = st.slider("Timeout (saniye)", 5, 60, 30)
    
    if st.button("🔄 Ayarları Kaydet"):
        add_log(f"Settings updated: threads={thread_count}, timeout={timeout}")
        st.success("Ayarlar kaydedildi!")

# Ana içerik alanı
col1, col2, col3 = st.columns(3)

# İstatistikler
total_devices, online_devices, offline_devices = get_device_stats()

with col1:
    st.metric(
        label="📊 Toplam Cihaz",
        value=total_devices,
        delta=None
    )

with col2:
    st.metric(
        label="✅ Online Cihazlar",
        value=online_devices,
        delta=f"{online_devices}/{total_devices}"
    )

with col3:
    st.metric(
        label="❌ Offline Cihazlar",
        value=offline_devices,
        delta=f"{offline_devices}/{total_devices}"
    )

# Ana dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Network Status Dashboard")
    
    # Cihaz durumu grafiği
    status_data = pd.DataFrame({
        'Status': ['Online', 'Offline'],
        'Count': [online_devices, offline_devices]
    })
    
    fig = px.pie(
        status_data, 
        values='Count', 
        names='Status',
        title="Cihaz Durumu Dağılımı",
        color_discrete_map={'Online': '#28a745', 'Offline': '#dc3545'}
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Cihaz listesi
    st.subheader("🖥️ Cihaz Listesi")
    
    devices_df = pd.DataFrame(st.session_state.devices)
    
    # Status sütununu renklendir
    def highlight_status(val):
        color = '#28a745' if val == 'Online' else '#dc3545'
        return f'color: {color}; font-weight: bold'
    
    styled_df = devices_df.style.applymap(highlight_status, subset=['status'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("🔧 Hızlı İşlemler")
    
    # Cihaz durumu kartları
    for device in st.session_state.devices:
        with st.container():
            status_color = "🟢" if device['status'] == 'Online' else "🔴"
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1rem;
                border-radius: 10px;
                margin: 0.5rem 0;
                color: white;
            ">
                <h4>{status_color} {device['name']}</h4>
                <p>IP: {device['ip']}</p>
                <p>Type: {device['type']}</p>
                <p>Status: {device['status']}</p>
            </div>
            """, unsafe_allow_html=True)

# Log alanı
st.subheader("📋 Canlı Loglar")

# Log kontrolü
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🗑️ Logları Temizle"):
        st.session_state.logs = []
        add_log("Logs cleared")
        st.rerun()

# Log görüntüleme
log_container = st.container()
with log_container:
    log_text = "\n".join(st.session_state.logs[-20:])  # Son 20 log
    st.text_area(
        "Sistem Logları",
        value=log_text,
        height=300,
        disabled=True
    )

# Alt bilgi
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.info("💡 **İpucu**: Sidebar'dan görevleri başlatabilirsiniz")

with col2:
    st.info("📊 **Durum**: Sistem hazır ve çalışır durumda")

with col3:
    st.info(f"🕐 **Son Güncelleme**: {datetime.now().strftime('%H:%M:%S')}")

# Otomatik yenileme (isteğe bağlı)
if st.checkbox("🔄 Otomatik Yenileme (10 saniye)"):
    time.sleep(10)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>NetPilot v2.0 - Network Automation Suite | Made with ❤️ using Streamlit</p>
    </div>
    """, 
    unsafe_allow_html=True
)
