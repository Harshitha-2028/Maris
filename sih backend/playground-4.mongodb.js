// SAMPLE QUERIES FOR YOUR BACKEND

// 1. Get all active projects
print("Active Projects:");
db.projects.find({status: "active"}).forEach(p => {
    print(`  ${p.name} (${p.project_type}) - ${p.balances.circulating} credits`);
});

// 2. Total credits issued across all projects
totalIssued = db.projects.aggregate([
    {$group: {_id: null, total: {$sum: "$balances.total_issued"}}}
]).toArray()[0]?.total || 0;
print(`\nTotal credits issued: ${totalIssued}`);

// 3. Recent transactions
print("\nRecent Transactions:");
db.transactions.find().sort({timestamp: -1}).limit(3).forEach(tx => {
    print(`  ${tx.type}: ${tx.details.project_id} (${tx.details.amount || 'N/A'} credits)`);
});

// 4. Users by role
print("\nUsers by Role:");
db.users.aggregate([
    {$group: {_id: "$profile.role", count: {$sum: 1}}},
    {$sort: {count: -1}}
]).forEach(role => {
    print(`  ${role._id}: ${role.count} users`);
});