import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, StatusBar, SafeAreaView } from 'react-native';
import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue } from 'firebase/database';

// A injeção das suas chaves (Extraídas do painel web)
const firebaseConfig = {
  apiKey: "AIzaSyD9q5bLMf7ytGEMS0Z0txIZCYziI0pdk9Y",
  databaseURL: "https://vbi-cloud-b7f78-default-rtdb.firebaseio.com",
};

// Inicializando o SDK do Google Firebase
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

export default function App() {
  const [data, setData] = useState({
    vazao: "0",
    total_parcial: "0",
    total_geral: "0",
    velocidade: "0.00",
    executando: false
  });
  const [statusCloud, setStatusCloud] = useState("Conectando nuvem...");

  useEffect(() => {
    // Apontando para o nó /balanca01 da sua Balança
    const balancaRef = ref(db, 'balanca01/');
    
    // ONVALUE: Fica escutando para sempre, sem precisar ficar fazendo "Requests". Se o ESP32 mexer, ativa.
    const unsubscribe = onValue(balancaRef, (snapshot) => {
      const val = snapshot.val();
      if (val) {
        setStatusCloud("Recepção Online");
        setData({
          vazao: val.vazao !== undefined ? String(val.vazao) : "0",
          total_parcial: val.total_parcial !== undefined ? String(val.total_parcial) : "0",
          total_geral: val.total_geral !== undefined ? String(val.total_geral) : "0",
          velocidade: val.velocidade !== undefined ? String(val.velocidade) : "0.00",
          executando: val.executando || false
        });
      } else {
        setStatusCloud("Aguardando ESP32...");
      }
    }, (error) => {
      setStatusCloud("Erro de conexão");
    });

    return () => unsubscribe();
  }, []);

  // Micro-Componente de Box (Semelhante à classe 'create_field' do nosso VBI Python)
  const NumericDisplay = ({ label, value, unit, color }) => (
    <View style={styles.fieldContainer}>
      <Text style={styles.lblLabel}>{label}</Text>
      <View style={styles.valContainer}>
        <Text style={[styles.valText, { color: color }]} numberOfLines={1} adjustsFontSizeToFit>
          {value}
        </Text>
        <Text style={styles.lblUnit}>{unit}</Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0000FF" />
      
      {/* Top Bar Azul Idêntica */}
      <View style={styles.topBar}>
        <Text style={styles.topTitle}>Operação</Text>
      </View>

      <View style={styles.body}>
        <Text style={styles.appTitle}>Esteira</Text>
        
        {/* Vazão */}
        <NumericDisplay label="Vazão" value={data.vazao} unit="t/h" color="white" />

        {/* Tag Executando Idêntica ao Qt */}
        <View style={styles.tagContainer}>
          <Text style={[styles.tagExec, data.executando ? styles.tagExecON : styles.tagExecOFF]}>
            {data.executando ? "Executando" : "Parada"}
          </Text>
        </View>

        {/* Parcial */}
        <NumericDisplay label="Totalizador Parcial" value={data.total_parcial} unit="t" color="#00FF00" />
        
        {/* Geral */}
        <NumericDisplay label="Totalizador Geral" value={data.total_geral} unit="t" color="yellow" />
        
        {/* Velocidade */}
        <NumericDisplay label="Velocidade" value={data.velocidade} unit="m/seg" color="cyan" />
      </View>

      {/* Nossa Status Bar para verificação da Nuvem */}
      <View style={styles.statusBarContainer}>
        <Text style={styles.statusBarText}>{statusCloud}</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#888888', // Fundo cinza liso
  },
  topBar: {
    backgroundColor: '#0000FF',
    height: 60,
    justifyContent: 'center',
    paddingHorizontal: 15,
  },
  topTitle: {
    color: 'white',
    fontSize: 22,
    fontWeight: 'bold',
  },
  body: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
  },
  appTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#000',
  },
  fieldContainer: {
    width: '100%',
    marginBottom: 15,
  },
  lblLabel: {
    fontSize: 18,
    marginBottom: 5,
    color: '#000',
  },
  valContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  valText: {
    flex: 1,
    backgroundColor: 'black',
    fontSize: 40,
    fontWeight: 'bold',
    textAlign: 'right',
    paddingRight: 10,
    paddingVertical: 5,
    overflow: 'hidden',
  },
  lblUnit: {
    fontSize: 18,
    marginLeft: 10,
    width: 60,
    color: '#000',
  },
  tagContainer: {
    width: '100%',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  tagExec: {
    fontSize: 16,
    fontWeight: 'bold',
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderWidth: 1,
    borderColor: 'white',
    backgroundColor: '#666666',
  },
  tagExecON: {
    color: '#00FF00',
  },
  tagExecOFF: {
    color: 'red',
  },
  statusBarContainer: {
    backgroundColor: '#DDDDDD',
    paddingVertical: 5,
    paddingHorizontal: 10,
    borderTopWidth: 1,
    borderTopColor: '#555',
  },
  statusBarText: {
    fontSize: 14,
    color: '#000',
  }
});
