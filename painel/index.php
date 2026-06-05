<?php
$db = new SQLite3("dadosSQL.db");

$TOTAL_VAGAS = 100;

/* =========================
   SNAPSHOT
========================= */
$snap = $db->querySingle(
    "SELECT * FROM snapshot ORDER BY id DESC LIMIT 1",
    true
);

$ocupadas = $snap['ocupadas'] ?? 0;
$entradas = $snap['entradas'] ?? 0;
$saidas = $snap['saidas'] ?? 0;

$ocupacao = ($TOTAL_VAGAS > 0)
    ? round(($ocupadas / $TOTAL_VAGAS) * 100, 1)
    : 0;

/* =========================
   CANCELA
========================= */
$cancela = $db->querySingle(
    "SELECT valor FROM sistema WHERE chave='cancela'",
    false
);

$cancela = $cancela ?: 'UNKNOWN';

if ($cancela === 'OPEN') {
    $cancela_texto = 'ABERTA';
    $cancela_cor = '#2ecc71'; 
} elseif ($cancela === 'OFFLINE') {
    $cancela_texto = 'OFFLINE';
    $cancela_cor = '#e74c3c'; 
} else {
    $cancela_texto = 'FECHADA';
    $cancela_cor = '#e74c3c'; 
}

/* =========================
   VAGAS
========================= */
$vagas = [];
$result = $db->query("SELECT id, ocupada FROM vagas ORDER BY id ASC");

while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
    $vagas[$row['id']] = $row['ocupada'];
}

/* =========================
   LAYOUT FIXO 10x10 (100 vagas)
========================= */
$layout = array_fill(0, 10, 10);

$id = 1;
?>



<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Super Estacionamento</title>

<style>
body {
    margin: 0;
    font-family: Arial;
    background: #111;
    color: white;
}

/* =========================
   PAINEL TOPO
========================= */
.top-info {
    position: absolute;
    top: 20px;
    left: 20px;
    background: #222;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 15px;
    line-height: 1.4;
}

/* barra ocupação */
.bar {
    width: 180px;
    height: 8px;
    background: #333;
    border-radius: 5px;
    margin-top: 8px;
    overflow: hidden;
    
}

.fill {
    height: 100%;
    background: #3498db;
    transition: width 0.3s ease;
    
}

/* =========================
   CENTRAL
========================= */
.center-box {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    
}

/* =========================
   ESTACIONAMENTO (REALISTA)
========================= */
.parking {
    background: #1c1c1c;
    padding: 50px;
    border-radius: 40px;
    border: 5px solid #333;
    box-shadow: 0 0 25px rgba(0,0,0,0.6);
    transform: rotate(-90deg);
    margin-top: -120px;
}

/* entrada / saída */
.entry, .exit {
    
    color: #888;
    font-size: 23px;
    margin: 15px 0;

}


/* =========================
   FILEIRAS (BLOCOS)
========================= */
.row {
    display: flex;
    justify-content: center;
    gap: 6px;
    margin-bottom: 8px;
    padding: 12px 4px;
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    position: relative;
}

/* linha divisória tipo “faixa” */
.row::after {
    content: "";
    position: absolute;
    bottom: -4px;
    left: 10%;
    width: 80%;
    height: 2px;
    background: repeating-linear-gradient(
        90deg,
        #444,
        #444 8px,
        transparent 8px,
        transparent 16px
    );
    opacity: 0.5;
}

/* =========================
   VAGAS
========================= */
.car {
    width: 58px;
    height: 38px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: bold;
    transition: 0.2s;
}

.car:hover {
    transform: scale(1.15);
    
}

/* livre */
.free {
    background: #2ecc71;
    box-shadow: 0 0 6px rgba(46,204,113,0.6);
    transform: rotate(65deg);

}

/* ocupada */
.occupied {
    background: #e74c3c;
    box-shadow: 0 0 6px rgba(231,76,60,0.6);
    transform: rotate(90deg);
}

/* =========================
   CORREDORES (rua principal)
========================= */
.aisle {
    height: 28px;
    position: relative;
}

.aisle::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 5%;
    width: 90%;
    height: 4px;
    background: repeating-linear-gradient(
        90deg,
        #555,
        #555 12px,
        transparent 12px,
        transparent 24px
    );
    transform: translateY(-50%);
    opacity: 0.7;
}
</style>
</head>



<!-- Recarregar a cada 30 segundos -->
<script>
setTimeout(() => {
    location.reload();
}, 3000); // 70 segundos
</script>


<body>

<!-- PAINEL -->
<div class="top-info">
    🚗 Entradas: <?= $entradas ?><br>
    🚪 Saídas: <?= $saidas ?><br>
    📊 Ocupação: <?= $ocupacao ?>%<br>
    🚧 Cancela:
    <span style="color: <?= $cancela_cor ?>">
        <?= $cancela_texto ?>
    </span>

    <div class="bar">
        <div class="fill" style="width: <?= $ocupacao ?>%"></div>
    </div>
</div>

<!-- ESTACIONAMENTO -->
<div class="center-box">
    <div class="parking">

        <div class="entry" >⬇ ENTRADA</div>

        <?php foreach ($layout as $rowSize): ?>
            <div class="row">

                <?php for ($i = 0; $i < $rowSize; $i++): ?>

                    <?php $ocupada = $vagas[$id] ?? 0; ?>

                    <div class="car <?= $ocupada ? 'occupied' : 'free' ?>">
                        <span style="display:inline-block; transform: rotate(90deg);">
                            <?= $id ?>
                        </span>
                    </div>

                    <?php $id++; ?>

                <?php endfor; ?>

            </div>

            <div class="aisle"></div>

        <?php endforeach; ?>

        <div class="exit">⬇ SAÍDA</div>

    </div>
</div>

</body>
</html>
