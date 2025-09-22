// upsert-plots.js
import { MongoClient } from "mongodb";
import fs from "fs";
import csv from "csv-parser";
import dotenv from "dotenv";

dotenv.config();

const uri = process.env.MONGO_URI;
const dbName = process.env.MONGO_DB || "bluecarbon";
const collectionName = "plots";
const csvFilePath = "./plots.csv"; // your input file

// helper: build Date and GeoJSON
const toDoc = (r) => ({
  ...r,
  GPS_Lat: parseFloat(r.GPS_Lat),
  GPS_Long: parseFloat(r.GPS_Long),
  Tree_Height_m: parseFloat(r.Tree_Height_m),
  DBH_cm: parseFloat(r.DBH_cm),
  Biomass_above_kg: parseFloat(r.Biomass_above_kg),
  Biomass_below_kg: parseFloat(r.Biomass_below_kg),
  Soil_Organic_Carbon_g_per_kg: parseFloat(r.Soil_Organic_Carbon_g_per_kg),
  Soil_Salinity_psu: parseFloat(r.Soil_Salinity_psu),
  Soil_Moisture_percent: parseFloat(r.Soil_Moisture_percent),
  Soil_pH: parseFloat(r.Soil_pH),
  Water_Salinity_psu: parseFloat(r.Water_Salinity_psu),
  Water_Temperature_C: parseFloat(r.Water_Temperature_C),
  CO2_Flux_mg_m2_day: parseFloat(r.CO2_Flux_mg_m2_day),
  CH4_Flux_mg_m2_day: parseFloat(r.CH4_Flux_mg_m2_day),
  NDVI: parseFloat(r.NDVI),
  Canopy_Cover_percent: parseFloat(r.Canopy_Cover_percent),
  Plot_Area_ha: parseFloat(r.Plot_Area_ha),
  Soil_Bulk_Density_g_cm3: parseFloat(r.Soil_Bulk_Density_g_cm3),
  Soil_Depth_cm: parseFloat(r.Soil_Depth_cm),
  Monitoring_Year: parseInt(r.Monitoring_Year),

  Timestamp: r.Timestamp ? new Date(r.Timestamp.replace(" ", "T") + "Z") : null,
  location: {
    type: "Point",
    coordinates: [parseFloat(r.GPS_Long), parseFloat(r.GPS_Lat)]
  },
  created_at: new Date(),
  updated_at: new Date()
});

async function main() {
  const client = new MongoClient(uri);

  try {
    await client.connect();
    const col = client.db(dbName).collection(collectionName);

    const rows = [];
    fs.createReadStream(csvFilePath)
      .pipe(csv())
      .on("data", (row) => rows.push(row))
      .on("end", async () => {
        console.log(`📥 Loaded ${rows.length} rows from CSV`);

        const ops = rows.map((r) => ({
          updateOne: {
            filter: { ID: r.ID },
            update: { $set: toDoc(r) },
            upsert: true
          }
        }));

        const res = await col.bulkWrite(ops, { ordered: false });
        console.log("✅ Upsert complete:", {
          upserted: res.upsertedCount,
          modified: res.modifiedCount,
          matched: res.matchedCount
        });

        await client.close();
      });
  } catch (e) {
    console.error("❌ Error:", e);
    await client.close();
  }
}

main();
