document.addEventListener("DOMContentLoaded", function () {
    const loggedIn = window.loggedIn || false;

    if (!loggedIn) {
        setTimeout(() => {
            alert("⚠️ Vui lòng đăng nhập hoặc đăng ký tài khoản để tiếp tục sử dụng trang web.");
            window.location.href = "/login";
        },  10000);
    }
});