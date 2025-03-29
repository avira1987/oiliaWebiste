// فعال‌سازی همه مودال‌های بوت‌استرپ
document.addEventListener('DOMContentLoaded', function() {
    // فعال‌سازی همه tooltip ها
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // فعال‌سازی همه popover ها
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // بستن خودکار پیام‌های هشدار بعد از 5 ثانیه
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// تابع برای نمایش پیام‌های موفقیت
function showSuccessMessage(message) {
    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
    setTimeout(function() {
        var bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// تابع برای نمایش پیام‌های خطا
function showErrorMessage(message) {
    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('main').insertBefore(alertDiv, document.querySelector('main').firstChild);
    setTimeout(function() {
        var bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// تابع برای تأیید حذف آیتم
function confirmDelete(message = 'آیا از حذف این مورد اطمینان دارید؟') {
    return confirm(message);
}

// تابع برای فرمت کردن اعداد فارسی
function formatNumber(number) {
    return new Intl.NumberFormat('fa-IR').format(number);
}

// تابع برای فرمت کردن تاریخ فارسی
function formatDate(date) {
    return new Intl.DateTimeFormat('fa-IR').format(new Date(date));
}

// تابع برای اعتبارسنجی شماره موبایل
function validatePhoneNumber(phone) {
    return /^09\d{9}$/.test(phone);
}

// تابع برای اعتبارسنجی شماره پلاک
function validatePlateNumber(plate) {
    return /^[0-9]{2}[A-Z]{3}[0-9]{2}$/.test(plate);
}

// تابع برای نمایش مودال لودینگ
function showLoading() {
    var loadingDiv = document.createElement('div');
    loadingDiv.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center bg-light bg-opacity-75';
    loadingDiv.style.zIndex = '9999';
    loadingDiv.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">در حال بارگذاری...</span>
        </div>
    `;
    document.body.appendChild(loadingDiv);
}

// تابع برای پنهان کردن مودال لودینگ
function hideLoading() {
    var loadingDiv = document.querySelector('.position-fixed');
    if (loadingDiv) {
        loadingDiv.remove();
    }
} 