// src/data/geography.js

export const JHARKHAND_DISTRICTS = [
    "Ranchi",
    "Dhanbad",
    "Jamshedpur", // Technically East Singhbhum but matching our mock data
    "Bokaro",
    "Dumka",
    "Deoghar",
    "Hazaribagh",
    "Giridih",
    "Latehar",
    "Gumla",
    "Simdega",
];

export const DOMAINS = [
    "HealthTech",
    "EdTech",
    "AgriTech",
    "BioTech",
    "Public Health",
    "Water Management",
    "Sanitation",
    "Environment",
    "Urban Infrastructure",
    "Accessibility",
    "Public Administration",
    "Rural Livelihoods"
];

export const PRIORITIES = [
    { value: "critical", label: "Critical (85+)" },
    { value: "high", label: "High (70-84)" },
    { value: "medium", label: "Medium (50-69)" },
    { value: "low", label: "Low (<50)" }
];
