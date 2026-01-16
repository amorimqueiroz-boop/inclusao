import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

// Cole abaixo as chaves que você pegou no Firebase Console
const firebaseConfig = {
  apiKey: "AIzaSyAHpq3ADwQRJiIrJTpXYAyzB0sIQpLcLqQ",
  authDomain: "minisfera.firebaseapp.com",
  projectId: "ominisfera",
  storageBucket: "ominisfera.firebasestorage.app",
  messagingSenderId: "379434309154",
  appId: "1:379434309154:web:66227de16ca5384891dc7b",
  measurementId: "G-D7H55XRTTV"
};

// Inicializa o Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { auth, googleProvider };
