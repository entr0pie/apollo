<!DOCTYPE html>
<?php

ini_set('display_startup_errors', 1);
ini_set('display_errors', 1);
error_reporting(-1);

?>
<html>
<head>
    <title>Request Information</title>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h2>Request Information</h2>

    <table>
        <tr>
            <th>Method</th>
            <th>IP Address</th>
            <th>Start Line</th>
        </tr>
        <tr>
            <td><?php echo $_SERVER['REQUEST_METHOD']; ?></td>
            <td><?php echo $_SERVER['REMOTE_ADDR']; ?></td>
            <td><?php echo $_SERVER['REQUEST_URI']; ?></td>
        </tr>
    </table>

    <h3>Headers</h3>

    <table>
        <tr>
            <th>Header</th>
            <th>Value</th>
        </tr>
        <?php
            foreach (getallheaders() as $name => $value) {
                echo "<tr><td>{$name}</td><td>{$value}</td></tr>";
            }
        ?>
    </table>

    <?php if ($_SERVER['REQUEST_METHOD'] === 'POST'): ?>
        <h3>Body</h3>

        <?php if (strpos($_SERVER['CONTENT_TYPE'], 'application/x-www-form-urlencoded') !== false): ?>
            <pre><?php echo http_build_query($_POST); ?></pre>
        <?php elseif (strpos($_SERVER['CONTENT_TYPE'], 'application/json') !== false): ?>
          <?php
            $input = file_get_contents('php://input');
            $data = json_decode($input, true);
            $json = json_encode($data, JSON_PRETTY_PRINT);
          ?>
          <pre><?php echo $json; ?></pre>
        <?php endif; ?>
    <?php endif; ?>
</body>
</html>

