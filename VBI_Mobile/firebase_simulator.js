const { initializeApp } = require('firebase/app');
const { getDatabase, ref, set } = require('firebase/database');

const firebaseConfig = {
  apiKey: "AIzaSyD9q5bLMf7ytGEMS0Z0txIZCYziI0pdk9Y",
  databaseURL: "https://vbi-cloud-b7f78-default-rtdb.firebaseio.com",
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

let vazao = 120;
let total_parcial = 400;
let total_geral = 15000;
let velocidade = 2.45;

console.log("Simulador Ligado! Injetando dados realistas na Nuvem do Firebase a cada 1 segundo...");
console.log("Abra o Aplicativo no celular e observe a mágica!");

setInterval(() => {
  vazao = vazao + (Math.random() * 4 - 2);
  vazao = Math.max(10, vazao); // Vazao never drops below 10 for realism
  
  total_parcial += (vazao / 3600);
  total_geral += (vazao / 3600);
  velocidade = 2.45 + (Math.random() * 0.1 - 0.05);

  set(ref(db, 'balanca01/'), {
    vazao: Math.round(vazao),
    total_parcial: Math.round(total_parcial),
    total_geral: Math.round(total_geral),
    velocidade: velocidade.toFixed(2),
    executando: true
  }).catch(err => {
    // Silently ignore errors or log them if needed
  });
  
  process.stdout.write(`Vazão injetada: ${Math.round(vazao)} t/h\r`);
}, 1000);
