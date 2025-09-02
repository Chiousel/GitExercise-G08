function getUsers() {
  return JSON.parse(localStorage.getItem("users")) || {};
}

function saveUsers(users) {
  localStorage.setItem("users", JSON.stringify(users));
}

function register() {
  const email = document.getElementById("regEmail").value;
  const password = document.getElementById("regPassword").value;
  const regMsg = document.getElementById("regMsg");

  let users = getUsers();

  if (!email.endsWith("@student.mmu.edu.my")) {
    regMsg.textContent = "Only MMU students can register!";
    regMsg.style.color = "red";
    return;
  }

  if (password.length < 6) {
    regMsg.textContent = "Password must be at least 6 characters!";
    regMsg.style.color = "red";
    return;
  }

  if (users[email]) {
    regMsg.textContent = "User already exists!";
    regMsg.style.color = "red";
  } else {
    users[email] = password;
    saveUsers(users);
    regMsg.style.color = "green";
    regMsg.textContent = "Registration successful!";
  }
}

function login() {
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;
  const loginMsg = document.getElementById("loginMsg");

  let users = getUsers();

  if (!email.endsWith("@student.mmu.edu.my")) {
    loginMsg.textContent = "Invalid MMU email!";
    loginMsg.style.color = "red";
    return;
  }

  if (users[email] && users[email] === password) {
    document.getElementById("loginDiv").style.display = "none";
    document.getElementById("registerDiv").style.display = "none";
    document.getElementById("welcomeDiv").style.display = "block";
    document.getElementById("userEmail").textContent = email;
  } else {
    loginMsg.textContent = "Incorrect email or password!";
    loginMsg.style.color = "red";
  }
}

function logout() {
  document.getElementById("welcomeDiv").style.display = "none";
  document.getElementById("loginDiv").style.display = "block";
  document.getElementById("registerDiv").style.display = "block";
}
