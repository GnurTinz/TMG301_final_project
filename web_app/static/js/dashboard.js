/**
 * JavaScript for Model Analytics Dashboard (TMG301).
 */

document.addEventListener("DOMContentLoaded", () => {
  const benchmarkTableBody = document.getElementById("benchmarkTableBody");
  const modelSelectorRow = document.getElementById("modelSelectorRow");
  const selectedModelBadge = document.getElementById("selectedModelBadge");
  const perClassTableBody = document.getElementById("perClassTableBody");
  const cmGridContainer = document.getElementById("cmGridContainer");

  const plotGalleryTabs = document.getElementById("plotGalleryTabs");
  const activePlotImg = document.getElementById("activePlotImg");
  const activePlotTitle = document.getElementById("activePlotTitle");
  const activePlotDesc = document.getElementById("activePlotDesc");

  let dashboardData = null;
  let activeModelKey = "Support Vector Machine (LinearSVC)";
  let activePlotId = "model_compare";

  const CLASS_LABELS = [
    { key: "Technical Issue", vi: "Lỗi kỹ thuật", dept: "Phòng Hỗ trợ Kỹ thuật" },
    { key: "Payment", vi: "Thanh toán & Giao dịch", dept: "Phòng Kế toán & Thanh toán" },
    { key: "Return/Refund", vi: "Đổi trả & Hoàn tiền", dept: "Phòng CSKH & Đổi trả" }
  ];

  async function initDashboard() {
    try {
      const res = await fetch("/api/dashboard-data");
      const json = await res.json();
      if (!json.success) {
        console.error("Lỗi nạp dashboard data:", json.error);
        return;
      }
      dashboardData = json;

      renderBenchmarkTable();
      renderModelSelector();
      renderModelDetails(activeModelKey);
      renderPlotGallery();
    } catch (err) {
      console.error("Không thể kết nối API dashboard:", err);
    }
  }

  // 1. Render Bảng So sánh Tất cả Mô hình
  function renderBenchmarkTable() {
    const models = dashboardData.models_summary;
    const sortedKeys = Object.keys(models).sort((a, b) => models[b].macro_f1 - models[a].macro_f1);

    const medals = ["🥇 Quán quân", "🥈 Á quân", "🥉 Hạng 3", "Hạng 4"];

    benchmarkTableBody.innerHTML = sortedKeys.map((key, idx) => {
      const m = models[key];
      const isWinner = idx === 0;

      let statusBadge = `<span class="badge-tag" style="background: rgba(255,255,255,0.06); color: #cbd5e1;">Đã đánh giá</span>`;
      if (isWinner) {
        statusBadge = `<span class="badge-tag" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">🏆 Tối ưu nhất (Production)</span>`;
      } else if (key.includes("Baseline")) {
        statusBadge = `<span class="badge-tag" style="background: rgba(59, 130, 246, 0.2); color: #60a5fa;">Baseline chuẩn</span>`;
      }

      return `
        <tr style="${isWinner ? 'background: rgba(59, 130, 246, 0.08);' : ''}">
          <td><strong>${medals[idx] || (idx + 1)}</strong></td>
          <td>
            <strong style="color: #fff; font-size: 0.95rem;">${key}</strong>
          </td>
          <td><strong style="color: #38bdf8; font-size: 1rem;">${(m.accuracy * 100).toFixed(2)}%</strong></td>
          <td>${(m.balanced_accuracy * 100).toFixed(2)}%</td>
          <td><strong style="color: #34d399;">${(m.macro_f1 * 100).toFixed(2)}%</strong></td>
          <td>${(m.weighted_f1 * 100).toFixed(2)}%</td>
          <td>${(m.macro_precision * 100).toFixed(2)}%</td>
          <td>${(m.macro_recall * 100).toFixed(2)}%</td>
          <td style="font-family: monospace;">${m.train_time_sec.toFixed(2)}s</td>
          <td>${statusBadge}</td>
        </tr>
      `;
    }).join("");
  }

  // 2. Render Bộ Chọn Mô Hình (Model Selector Tabs)
  function renderModelSelector() {
    const models = dashboardData.models_summary;
    const sortedKeys = Object.keys(models).sort((a, b) => models[b].macro_f1 - models[a].macro_f1);

    modelSelectorRow.innerHTML = sortedKeys.map(key => {
      const shortName = key.replace("Support Vector Machine ", "").replace(" (Baseline)", "");
      return `
        <button type="button" class="model-tab-btn ${key === activeModelKey ? 'active' : ''}" data-model="${key}">
          ${shortName}
        </button>
      `;
    }).join("");

    modelSelectorRow.querySelectorAll(".model-tab-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        modelSelectorRow.querySelectorAll(".model-tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        activeModelKey = btn.dataset.model;
        renderModelDetails(activeModelKey);
      });
    });
  }

  // 3. Render Chi tiết Model & Confusion Matrix
  function renderModelDetails(modelKey) {
    selectedModelBadge.textContent = modelKey;
    const m = dashboardData.models_summary[modelKey];
    if (!m) return;

    const rep = m.classification_report;

    // A. Bảng Per-Class Metrics
    perClassTableBody.innerHTML = CLASS_LABELS.map(c => {
      const stats = rep[c.key] || { precision: 0, recall: 0, "f1-score": 0, support: 0 };
      return `
        <tr>
          <td><strong style="color: #fff;">${c.dept}</strong></td>
          <td><span class="badge-tag ${c.key === 'Technical Issue' ? 'badge-tech' : (c.key === 'Payment' ? 'badge-payment' : 'badge-refund')}">${c.key}</span></td>
          <td><strong style="color: #38bdf8;">${(stats.precision * 100).toFixed(2)}%</strong></td>
          <td>${(stats.recall * 100).toFixed(2)}%</td>
          <td><strong style="color: #34d399;">${(stats['f1-score'] * 100).toFixed(2)}%</strong></td>
          <td style="font-family: monospace;">${stats.support.toLocaleString()} mẫu</td>
        </tr>
      `;
    }).join("");

    // B. Ma Trận Nhầm Lẫn Grid
    renderConfusionMatrixGrid(m.confusion_matrix);
  }

  function renderConfusionMatrixGrid(matrix) {
    const labels = ["Payment", "Return/Refund", "Technical Issue"];
    const viLabels = ["Thanh toán", "Đổi trả", "Kỹ thuật"];

    let html = `
      <div class="cm-header-cell">Thực tế \\ Dự đoán</div>
      ${viLabels.map(l => `<div class="cm-header-cell">${l}</div>`).join("")}
    `;

    for (let r = 0; r < 3; r++) {
      html += `<div class="cm-header-cell" style="text-align: right; justify-content: flex-end; padding-right: 10px;">${viLabels[r]}</div>`;
      
      const rowSum = matrix[r][0] + matrix[r][1] + matrix[r][2];
      for (let c = 0; c < 3; c++) {
        const val = matrix[r][c];
        const pct = (val / rowSum * 100).toFixed(1);
        const isDiagonal = (r === c);

        let cellBg = isDiagonal ? `rgba(16, 185, 129, ${0.15 + (val / rowSum) * 0.4})` : (val > 0 ? `rgba(239, 68, 68, 0.15)` : `rgba(255, 255, 255, 0.02)`);
        let cellColor = isDiagonal ? "#34d399" : (val > 0 ? "#f87171" : "#64748b");

        html += `
          <div class="cm-cell" style="background: ${cellBg}; color: ${cellColor}; border: 1px solid ${isDiagonal ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.04)'};">
            <div>${val.toLocaleString()}</div>
            <div class="cm-cell-sub">(${pct}%)</div>
          </div>
        `;
      }
    }

    cmGridContainer.innerHTML = html;
  }

  // 4. Render Thư viện Đồ thị Nghiên cứu
  function renderPlotGallery() {
    const plots = dashboardData.plots || [];
    plotGalleryTabs.innerHTML = plots.map(p => `
      <button type="button" class="plot-tab-btn ${p.id === activePlotId ? 'active' : ''}" data-id="${p.id}">
        ${p.title}
      </button>
    `).join("");

    plotGalleryTabs.querySelectorAll(".plot-tab-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        plotGalleryTabs.querySelectorAll(".plot-tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        activePlotId = btn.dataset.id;

        const currentPlot = plots.find(p => p.id === activePlotId);
        if (currentPlot) {
          activePlotImg.src = `/plots/${currentPlot.filename}`;
          activePlotTitle.textContent = currentPlot.title;
          activePlotDesc.textContent = currentPlot.description;
        }
      });
    });
  }

  // Khởi động
  initDashboard();
});
