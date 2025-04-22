export async function loadCoveredWalkways() {
    try {
      const [allData, westData] = await Promise.all([
        fetch("/data/covered_walkways.geojson").then((res) => res.json()),
        fetch("/data/covered_walkways_west.geojson").then((res) => res.json()),
      ]);

      // console.log("features:", [...allData.features, ...westData.features]);
  
      return {
        type: "FeatureCollection",
        features: [...allData.features, ...westData.features],
      };
    } catch (err) {
      console.error("Failed to load covered walkways:", err);
      return null;
    }
  }
  