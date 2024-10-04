document
  .getElementById("searchForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    // Получаем значения артистов из формы
    const artist1 = document.getElementById("artist1").value;
    const artist2 = document.getElementById("artist2").value;

    // Отправляем запрос к API
    try {
      const response = await fetch(
        `/search_path/?artist_1=${encodeURIComponent(artist1)}&artist_2=${encodeURIComponent(artist2)}`
      );
      const data = await response.json();

      // Передаем данные в функцию для построения графа
      drawGraph(data);
    } catch (error) {
      console.error("Error fetching graph data:", error);
    }
  });

function drawGraph(graphData) {
  // Очищаем контейнер перед созданием нового графа
  const container = document.getElementById("graphContainer");
  container.innerHTML = "";

  // Используем библиотеку vis.js для отображения графа
  const nodes = new vis.DataSet(graphData.nodes);
  const edges = new vis.DataSet(graphData.edges);

  const data = {
    nodes: nodes,
    edges: edges,
  };

  const options = {
    interaction: {
      zoomView: true,
      dragView: true,
    },
    edges: {
      smooth: true,
    },
    nodes: {
      shape: "circle",
      size: 20,
      font: {
        size: 16,
      },
    },
  };

  const network = new vis.Network(container, data, options);
}
