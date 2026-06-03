<?php
$db = new SQLite3("dadosSQL.db");

// pega vagas
$vagas = [];
$result = $db->query("SELECT id, ocupada FROM vagas ORDER BY id ASC");

while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
    $vagas[$row['id']] = $row['ocupada'];
}

// pega último snapshot (entradas/saídas)
$snap = $db->querySingle(
    "SELECT entradas, saidas FROM snapshot ORDER BY id DESC LIMIT 1",
    true
);

$entradas = $snap['entradas'] ?? 0;
$saidas = $snap['saidas'] ?? 0;
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Smart Parking</title>

<style>
body {
    margin: 0;
    font-family: Arial;
    background: #111;
    color: white;
}

/* topo esquerdo */
.top-info {
    position: absolute;
    top: 20px;
    left: 20px;
    font-size: 18px;
    background: #222;
    padding: 10px 15px;
    border-radius: 8px;
}

/* centraliza tudo */
.center-box {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

/* grid 10x10 */
.grid {
    display: grid;
    grid-template-columns: repeat(10, 40px);
    grid-gap: 6px;
    padding: 20px;
    background: #222;
    border-radius: 10px;
}

/* vaga */
.car {
    width: 40px;
    height: 40px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: bold;
}

/* cores */
.occupied {
    background: red;
}

.free {
    background: green;
}
</style>

</head>

<body>

<!-- INFO TOPO ESQUERDO -->
<div class="top-info">
    Entradas: <?php echo $entradas; ?><br>
    Saídas: <?php echo $saidas; ?>
</div>

<!-- GRID CENTRAL -->
<div class="center-box">
    <div class="grid">

        <?php for ($i = 1; $i <= 100; $i++): ?>
            <div class="car <?php echo $vagas[$i] ? 'occupied' : 'free'; ?>">
                <?php echo $i; ?>
            </div>
        <?php endfor; ?>

    </div>
</div>

</body>
</html>