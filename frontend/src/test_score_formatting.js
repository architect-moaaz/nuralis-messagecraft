// Test script to verify score formatting works correctly

import { formatScore, getScoreColor } from './utils/formatters.js';

// Test cases
const testScores = [
  8.5,      // Should show: 8.50
  7.23456,  // Should show: 7.23
  9,        // Should show: 9.00
  6.1,      // Should show: 6.10
  "8.75",   // Should show: 8.75
  null,     // Should show: N/A
  "",       // Should show: N/A
  "invalid" // Should show: invalid
];

console.log("🎯 Score Formatting Test Results:");
console.log("=" * 40);

testScores.forEach(score => {
  const formatted = formatScore(score);
  const color = getScoreColor(score);
  console.log(`Score: ${score} → Formatted: ${formatted} → Color: ${color}`);
});

console.log("\n✅ Expected UI Changes:");
console.log("- All scores will now show exactly 2 decimal places");
console.log("- 8.5 becomes 8.50, 9 becomes 9.00, etc.");
console.log("- Color coding: Green (≥8.00), Yellow (≥6.00), Red (<6.00)");

export { formatScore, getScoreColor };