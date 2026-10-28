import os
import matplotlib.pyplot as plt
import numpy as np

os.makedirs('slide_assets', exist_ok=True)

# 1. Bank Card / Fraud alert notification mockup
fig, ax = plt.subplots(figsize=(6, 4.5), dpi=200)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')
# Draw a phone-style notification box
box = plt.Rectangle((0.08, 0.15), 0.84, 0.7, facecolor='#1e293b', edgecolor='#ef4444', linewidth=2.5, transform=ax.transAxes, zorder=2)
ax.add_patch(box)
ax.text(0.14, 0.72, "⚠️ Chase Fraud Alert", color='#f87171', fontsize=14, weight='bold', transform=ax.transAxes)
ax.text(0.14, 0.58, "Did you just attempt a $1,850 charge at\nApple Store Tokyo, JP?", color='#f8fafc', fontsize=12, transform=ax.transAxes)
ax.text(0.14, 0.40, "Last approved: 9:15 AM (Dallas, TX)\nAttempted: 9:42 AM (Tokyo, JP)", color='#94a3b8', fontsize=10, family='monospace', transform=ax.transAxes)
# Buttons
btn1 = plt.Rectangle((0.14, 0.22), 0.32, 0.12, facecolor='#334155', edgecolor='#64748b', transform=ax.transAxes)
btn2 = plt.Rectangle((0.54, 0.22), 0.32, 0.12, facecolor='#dc2626', edgecolor='#ef4444', transform=ax.transAxes)
ax.add_patch(btn1)
ax.add_patch(btn2)
ax.text(0.30, 0.27, "YES, ME", color='#94a3b8', fontsize=10, weight='bold', ha='center', transform=ax.transAxes)
ax.text(0.70, 0.27, "NO, FRAUD", color='#ffffff', fontsize=10, weight='bold', ha='center', transform=ax.transAxes)
ax.axis('off')
plt.savefig('slide_assets/bank_alert.png', bbox_inches='tight', pad_inches=0.1, facecolor='#0f172a')
plt.close()

# 2. Impossible Travel World Map
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')
# Rough world landmass outlines / markers
ax.scatter([-96.8], [32.8], color='#38bdf8', s=180, zorder=5, label='Dallas (9:15 AM)')
ax.scatter([139.7], [35.7], color='#ef4444', s=180, zorder=5, label='Tokyo (9:42 AM)')
# Flight arc
x_arc = np.linspace(-96.8, 139.7, 100)
y_arc = 32.8 + (35.7 - 32.8)*((x_arc - (-96.8))/(139.7 - (-96.8))) + 35 * np.sin(np.pi * (x_arc - (-96.8))/(139.7 - (-96.8)))
ax.plot(x_arc, y_arc, color='#f87171', linestyle='--', linewidth=2.5, zorder=4)
ax.text(-96.8, 26, "📍 Dallas, TX\n9:15 AM (Laptop)", color='#38bdf8', fontsize=11, weight='bold', ha='center')
ax.text(139.7, 26, "🚨 Tokyo, JP\n9:42 AM (Tor)", color='#ef4444', fontsize=11, weight='bold', ha='center')
ax.text(20, 68, "✈️ 6,400 miles in 27 mins = 14,200 MPH\n(Unless user owns an SR-71 Blackbird, this is a hack)", 
        color='#fde047', fontsize=10.5, weight='bold', ha='center',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#1e293b', edgecolor='#eab308', lw=1.5))
ax.set_xlim(-160, 180)
ax.set_ylim(-10, 85)
ax.axis('off')
plt.savefig('slide_assets/impossible_travel_map.png', bbox_inches='tight', pad_inches=0.1, facecolor='#0f172a')
plt.close()

# 3. Sock drawer visualization for Isolation Forest
fig, ax = plt.subplots(figsize=(6, 5), dpi=200)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')
# Draw drawer
drawer = plt.Rectangle((0.1, 0.1), 0.8, 0.8, facecolor='#1e293b', edgecolor='#475569', linewidth=3, transform=ax.transAxes)
ax.add_patch(drawer)
ax.text(0.5, 0.84, "THE SOCK DRAWER", color='#94a3b8', fontsize=12, weight='bold', ha='center', transform=ax.transAxes, family='monospace')
np.random.seed(42)
# 45 black/dark gray socks
for _ in range(45):
    rx = np.random.uniform(0.18, 0.82)
    ry = np.random.uniform(0.18, 0.75)
    circle = plt.Circle((rx, ry), 0.035, facecolor='#334155', edgecolor='#64748b', lw=1.5, transform=ax.transAxes)
    ax.add_patch(circle)
# 1 neon sock
neon = plt.Circle((0.48, 0.45), 0.045, facecolor='#facc15', edgecolor='#fef08a', lw=3, transform=ax.transAxes, zorder=6)
ax.add_patch(neon)
# Arrow pointing to neon sock
ax.annotate('Outlier (Isolated in 1 split!)', xy=(0.48, 0.45), xytext=(0.2, 0.22),
            textcoords='axes fraction', color='#fde047', weight='bold', fontsize=11,
            arrowprops=dict(arrowstyle="->", color='#fde047', lw=2), transform=ax.transAxes)
ax.axis('off')
plt.savefig('slide_assets/sock_drawer.png', bbox_inches='tight', pad_inches=0.1, facecolor='#0f172a')
plt.close()

# 4. The Boy Who Cried Wolf / Precision-Recall Alert Fatigue Illustration
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=200)
ax.set_facecolor('#0f172a')
fig.patch.set_facecolor('#0f172a')
# Bar comparison
bars = ax.bar(['Bad Model\n(High Recall, Low Precision)', 'Balanced Model\n(Our Isolation Forest)'], [94, 10], color=['#ef4444', '#10b981'], width=0.55, edgecolor='#ffffff', linewidth=1.5)
ax.set_ylabel('False Alarms Waking Up Analysts', color='#f8fafc', fontsize=11)
ax.tick_params(colors='#94a3b8', labelsize=10)
ax.grid(axis='y', linestyle=':', color='#334155', alpha=0.7)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{int(yval)} alerts / day", ha='center', va='bottom', color='#f8fafc', weight='bold', fontsize=11)
ax.text(0.5, 0.92, "🚨 The 'Boy Who Cried Wolf' Problem in SOCs:\nToo many false alarms = analysts ignore ALL alerts.", color='#fbbf24', fontsize=11, weight='bold', ha='center', transform=ax.transAxes,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#1e293b', edgecolor='#f59e0b', lw=1.2))
ax.set_ylim(0, 115)
plt.savefig('slide_assets/alert_fatigue.png', bbox_inches='tight', pad_inches=0.1, facecolor='#0f172a')
plt.close()

print("Assets generated successfully!")
