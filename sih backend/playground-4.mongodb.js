// SAMPLE QUERIES FOR YOUR BACKEND + PLOTS COLLECTION

// -------------------------------
// PROJECTS / TRANSACTIONS / USERS
// -------------------------------
use('bluecarbon');
db.plots.createIndex({ location: "2dsphere" });
// 1. Get all active projects
print("Active Projects:");
db.projects.find({ status: "active" }).forEach(p => {
  print(`  ${p.name} (${p.project_type}) - ${p.balances.circulating} credits`);
});

// 2. Total credits issued across all projects
let totalIssued = db.projects.aggregate([
  { $group: { _id: null, total: { $sum: "$balances.total_issued" } } }
]).toArray()[0]?.total || 0;
print(`\nTotal credits issued: ${totalIssued}`);

// 3. Recent transactions
print("\nRecent Transactions:");
db.transactions.find().sort({ timestamp: -1 }).limit(3).forEach(tx => {
  print(`  ${tx.type}: ${tx.details.project_id} (${tx.details.amount || 'N/A'} credits)`);
});

// 4. Users by role
print("\nUsers by Role:");
db.users.aggregate([
  { $group: { _id: "$profile.role", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]).forEach(role => {
  print(`  ${role._id}: ${role.count} users`);
});

// -------------------------------
// PLOTS COLLECTION ANALYSIS
// -------------------------------

// 5. Total number of plots
let plotCount = db.plots.countDocuments();
print(`\nTotal plots: ${plotCount}`);

// 6. Plots by Project_Type
print("\nPlots by Project_Type:");
db.plots.aggregate([
  { $group: { _id: "$Project_Type", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]).forEach(pt => {
  print(`  ${pt._id}: ${pt.count}`);
});

// 7. Average NDVI per Project_Type
print("\nAverage NDVI by Project_Type:");
db.plots.aggregate([
  { $group: { _id: "$Project_Type", avgNDVI: { $avg: "$NDVI" } } },
  { $sort: { avgNDVI: -1 } }
]).forEach(r => {
  print(`  ${r._id}: ${r.avgNDVI.toFixed(2)}`);
});

// 8. Geospatial query (plots within 10 km of point)
print("\nPlots near (90.944851, 1.236204) within 10km:");
db.plots.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [90.944851, 1.236204] },
      $maxDistance: 10000 // meters
    }
  }
}).limit(3).forEach(p => {
  print(`  ${p.ID} at [${p.GPS_Lat}, ${p.GPS_Long}]`);
});

// -------------------------------
// NEW TREND ANALYSIS QUERIES
// -------------------------------

// 9. Biomass trend by Monitoring_Year
print("\nBiomass (above + below ground) by Monitoring_Year:");
db.plots.aggregate([
  { $group: {
      _id: "$Monitoring_Year",
      avgBiomassAbove: { $avg: "$Biomass_above_kg" },
      avgBiomassBelow: { $avg: "$Biomass_below_kg" },
      totalBiomass: { $sum: { $add: ["$Biomass_above_kg", "$Biomass_below_kg"] } }
  }},
  { $sort: { _id: 1 } }
]).forEach(r => {
  print(`  Year ${r._id}: Above=${r.avgBiomassAbove.toFixed(1)}kg, Below=${r.avgBiomassBelow.toFixed(1)}kg, Total=${r.totalBiomass.toFixed(1)}kg`);
});

// 10. CO2 flux averages per year
print("\nAverage CO2 Flux (mg/m2/day) by Monitoring_Year:");
db.plots.aggregate([
  { $group: { _id: "$Monitoring_Year", avgCO2: { $avg: "$CO2_Flux_mg_m2_day" } } },
  { $sort: { _id: 1 } }
]).forEach(r => {
  print(`  Year ${r._id}: ${r.avgCO2.toFixed(2)} mg/m2/day`);
});

// 11. CH4 flux averages per year
print("\nAverage CH4 Flux (mg/m2/day) by Monitoring_Year:");
db.plots.aggregate([
  { $group: { _id: "$Monitoring_Year", avgCH4: { $avg: "$CH4_Flux_mg_m2_day" } } },
  { $sort: { _id: 1 } }
]).forEach(r => {
  print(`  Year ${r._id}: ${r.avgCH4.toFixed(2)} mg/m2/day`);
});

// 12. NDVI trend over time (monthly average)
print("\nNDVI monthly average trend:");
db.plots.aggregate([
  { $addFields: {
      month: { $month: "$Timestamp" },
      year: { $year: "$Timestamp" }
  }},
  { $group: {
      _id: { year: "$year", month: "$month" },
      avgNDVI: { $avg: "$NDVI" }
  }},
  { $sort: { "_id.year": 1, "_id.month": 1 } }
]).forEach(r => {
  print(`  ${r._id.year}-${r._id.month}: NDVI=${r.avgNDVI.toFixed(2)}`);
});
