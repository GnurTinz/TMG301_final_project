/**
 * Frontend JavaScript for Support Ticket Router CRM Web Demo.
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("ticketForm");
  const customerEmail = document.getElementById("customerEmail");
  const customerMessage = document.getElementById("customerMessage");
  const btnSubmit = document.getElementById("btnSubmit");
  const btnSpinner = document.getElementById("btnSpinner");
  const btnText = document.getElementById("btnText");
  const btnIcon = document.getElementById("btnIcon");

  const samplePillsContainer = document.getElementById("samplePills");
  const emptyState = document.getElementById("emptyState");
  const resultView = document.getElementById("resultView");

  // Result fields
  const ticketIdVal = document.getElementById("ticketIdVal");
  const deptBox = document.getElementById("deptBox");
  const deptCategoryPill = document.getElementById("deptCategoryPill");
  const priorityBadge = document.getElementById("priorityBadge");
  const deptNameVal = document.getElementById("deptNameVal");
  const deptCodeVal = document.getElementById("deptCodeVal");
  const viNameVal = document.getElementById("viNameVal");
  const slaHoursVal = document.getElementById("slaHoursVal");
  const confidenceVal = document.getElementById("confidenceVal");

  const barTech = document.getElementById("barTech");
  const valTech = document.getElementById("valTech");
  const barPayment = document.getElementById("barPayment");
  const valPayment = document.getElementById("valPayment");
  const barRefund = document.getElementById("barRefund");
  const valRefund = document.getElementById("valRefund");

  const responseBoxVal = document.getElementById("responseBoxVal");
  const btnCopyTicket = document.getElementById("btnCopyTicket");
  const btnCopyEmail = document.getElementById("btnCopyEmail");
  const btnNewTicket = document.getElementById("btnNewTicket");

  const historyTableBody = document.getElementById("historyTableBody");
  const btnClearHistory = document.getElementById("btnClearHistory");

  let recentHistory = JSON.parse(localStorage.getItem("crm_recent_tickets") || "[]");

  // 1. Nạp danh sách mẫu khiếu nại
  async function loadSamples() {
    try {
      const res = await fetch("/api/samples");
      const json = await res.json();
      if (json.success && json.samples) {
        renderSamplePills(json.samples);
      }
    } catch (err) {
      console.error("Không thể nạp samples:", err);
    }
  }

  function renderSamplePills(samples) {
    samplePillsContainer.innerHTML = "";
    samples.forEach(s => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "sample-btn";
      btn.innerHTML = `<span class="sample-tag">${s.tag}</span> <span>${s.subject}</span>`;
      btn.addEventListener("click", () => {
        customerEmail.value = s.sender;
        customerMessage.value = s.text;
        showToast(`Đã chọn mẫu: "${s.subject}"`);
      });
      samplePillsContainer.appendChild(btn);
    });
  }

  // 2. Xử lý gửi Form phân loại
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = customerMessage.value.trim();
    const email = customerEmail.value.trim();

    if (!msg) {
      showToast("Vui lòng nhập nội dung khiếu nại!", "warning");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/route-ticket", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          customer_email: email
        })
      });

      const res = await response.json();
      if (!res.success) {
        showToast(res.error || "Có lỗi xảy ra", "error");
        return;
      }

      displayRoutingResult(res.data);
      saveToHistory(res.data);
      showToast("Điều hướng CRM thành công!", "success");

    } catch (err) {
      console.error(err);
      showToast("Lỗi kết nối máy chủ", "error");
    } finally {
      setLoading(false);
    }
  });

  function setLoading(isLoading) {
    if (isLoading) {
      btnSubmit.disabled = true;
      btnSpinner.style.display = "inline-block";
      btnText.textContent = "Đang phân tích AI & điều hướng...";
      btnIcon.style.display = "none";
    } else {
      btnSubmit.disabled = false;
      btnSpinner.style.display = "none";
      btnText.textContent = "Phân loại & Điều hướng CRM";
      btnIcon.style.display = "inline";
    }
  }

  // 3. Hiển thị kết quả điều hướng
  function displayRoutingResult(data) {
    emptyState.style.display = "none";
    resultView.style.display = "block";

    const d = data.routing_decision;

    ticketIdVal.textContent = data.ticket_id;
    deptNameVal.textContent = d.target_department;
    deptCodeVal.textContent = `Mã phòng ban: ${d.dept_code}`;
    viNameVal.textContent = d.category_vi;
    slaHoursVal.textContent = `Trong ${d.sla_hours} giờ làm việc`;
    confidenceVal.textContent = `${d.confidence_score}%`;
    deptCategoryPill.textContent = d.category;

    // Đổi theme màu theo phòng ban
    deptBox.classList.remove("theme-tech", "theme-payment", "theme-refund");
    if (d.category === "Technical Issue") {
      deptBox.classList.add("theme-tech");
    } else if (d.category === "Payment") {
      deptBox.classList.add("theme-payment");
    } else {
      deptBox.classList.add("theme-refund");
    }

    // Priority badge
    priorityBadge.textContent = `Ưu tiên: ${d.priority_level}`;
    if (d.priority_level === "Urgent") {
      priorityBadge.style.background = "rgba(239, 68, 68, 0.25)";
      priorityBadge.style.color = "#f87171";
    } else if (d.priority_level === "High") {
      priorityBadge.style.background = "rgba(245, 158, 11, 0.25)";
      priorityBadge.style.color = "#fbbf24";
    } else {
      priorityBadge.style.background = "rgba(59, 130, 246, 0.25)";
      priorityBadge.style.color = "#60a5fa";
    }

    // Probability Bars
    const probs = d.all_class_probabilities || {};
    const pTech = probs["Technical Issue"] || 0;
    const pPay = probs["Payment"] || 0;
    const pRef = probs["Return/Refund"] || 0;

    barTech.style.width = `${pTech}%`;
    valTech.textContent = `${pTech.toFixed(1)}%`;

    barPayment.style.width = `${pPay}%`;
    valPayment.textContent = `${pPay.toFixed(1)}%`;

    barRefund.style.width = `${pRef}%`;
    valRefund.textContent = `${pRef.toFixed(1)}%`;

    // Response Box
    responseBoxVal.textContent = data.automated_response;

    // Cuộn nhẹ đến kết quả trên mobile
    if (window.innerWidth <= 992) {
      resultView.scrollIntoView({ behavior: "smooth" });
    }
  }

  // 4. Lưu và Hiển thị Lịch sử
  function saveToHistory(data) {
    const d = data.routing_decision;
    const item = {
      id: data.ticket_id,
      email: data.customer_email,
      snippet: data.customer_message.substring(0, 50) + (data.customer_message.length > 50 ? "..." : ""),
      category: d.category,
      category_vi: d.category_vi,
      dept: d.target_department,
      confidence: d.confidence_score,
      time: new Date().toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })
    };

    recentHistory.unshift(item);
    if (recentHistory.length > 8) recentHistory.pop();
    localStorage.setItem("crm_recent_tickets", JSON.stringify(recentHistory));
    renderHistory();
  }

  function renderHistory() {
    if (recentHistory.length === 0) {
      historyTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-dim); padding: 2rem;">Chưa có lịch sử điều hướng nào.</td></tr>`;
      return;
    }

    historyTableBody.innerHTML = recentHistory.map(item => {
      let badgeCls = "badge-tech";
      if (item.category === "Payment") badgeCls = "badge-payment";
      else if (item.category === "Return/Refund") badgeCls = "badge-refund";

      return `
        <tr>
          <td><strong style="font-family: monospace; color: #38bdf8;">${item.id}</strong></td>
          <td>${item.email}</td>
          <td style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${item.snippet}">${item.snippet}</td>
          <td><span class="badge-tag ${badgeCls}">${item.category}</span></td>
          <td>${item.dept}</td>
          <td><strong>${item.confidence}%</strong></td>
          <td style="color: var(--text-muted); font-size: 0.8rem;">${item.time}</td>
        </tr>
      `;
    }).join("");
  }

  btnClearHistory.addEventListener("click", () => {
    recentHistory = [];
    localStorage.removeItem("crm_recent_tickets");
    renderHistory();
    showToast("Đã xóa toàn bộ lịch sử");
  });

  // 5. Copy Buttons
  btnCopyTicket.addEventListener("click", () => {
    navigator.clipboard.writeText(ticketIdVal.textContent);
    showToast("Đã sao chép mã Ticket vào clipboard!");
  });

  btnCopyEmail.addEventListener("click", () => {
    navigator.clipboard.writeText(responseBoxVal.textContent);
    showToast("Đã sao chép email phản hồi vào clipboard!");
  });

  btnNewTicket.addEventListener("click", () => {
    customerMessage.value = "";
    customerMessage.focus();
    showToast("Đã sẵn sàng nhập ticket mới!");
  });

  // Toast Function
  function showToast(text, type = "info") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = "toast";
    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "❌";
    if (type === "warning") icon = "⚠️";

    toast.innerHTML = `<span>${icon}</span> <span>${text}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // Khởi động
  loadSamples();
  renderHistory();
});
