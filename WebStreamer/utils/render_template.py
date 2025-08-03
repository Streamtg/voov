<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{heading}</title>
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css">
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #141414;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        header {
            padding: 1rem;
            font-size: 1.5rem;
            font-weight: bold;
            background: #000;
            width: 100%;
            text-align: center;
        }
        main {
            width: 90%;
            max-width: 900px;
            margin-top: 2rem;
        }
        .download-btn {
            display: inline-block;
            background: #e50914;
            color: white;
            padding: 10px 18px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 10px;
        }
        .download-btn:hover {
            background: #b20710;
        }
    </style>
</head>
<body>
    <header>{heading}</header>
    <main>
        <video id="player" playsinline controls crossorigin>
            <source src="{src}" type="video/mp4">
            Tu navegador no soporta la reproducción de este archivo.
        </video>
        <a class="download-btn" href="{download_url}" download>⬇ Descargar</a>
    </main>

    <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
    <script>
        const player = new Plyr('#player', {
            controls: ['play', 'progress', 'current-time', 'mute', 'volume', 'fullscreen']
        });
    </script>
</body>
</html>
