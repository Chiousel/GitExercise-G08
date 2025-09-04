function showLogin() { window.location.href = "login.html"; }
function showRegister() { alert("Register form coming soon!"); }
function goLogin() { window.location.href = "login.html"; }

// 导航栏智能隐藏
(function(){
  const header = document.getElementById('site-header');
  let last = 0;
  const DELTA = 8;
  const HIDE_AT = 80;

  window.addEventListener('scroll', () => {
    const y = window.scrollY || document.documentElement.scrollTop;
    if (y - last > DELTA && y > HIDE_AT) {
      header.style.transform = 'translateY(-100%)';
    } else if (last - y > DELTA) {
      header.style.transform = 'translateY(0)';
    }
    last = y <= 0 ? 0 : y;
  }, { passive: true });
})();

// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});
