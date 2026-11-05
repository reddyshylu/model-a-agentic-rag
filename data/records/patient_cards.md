# Model A Patient Cards (30 fictional patients)

> FICTIONAL, NOT A REAL PATIENT. Synthetic data for the Model A demo.

Generated with seed 2026. Today in the demo is 2026-10-26. Last-visit lab results are held back and released during the demo.

| ID | Name | Age/Sex | Diagnosis | Stage | Watch | Designed alerts | Negative control |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | Rachel Kelley | 32/F | MASLD | F2 | no |  |  |
| P02 | Ernest Sanders | 60/M | MASLD | F2 | yes |  | ALT 1.8x baseline (below 2x) |
| P03 | Sarah Wood | 46/F | MASLD | F2 | yes | R07 alt double |  |
| P04 | Ryan Elliott | 42/M | MASLD | F1 | yes |  |  |
| P05 | Charles Wilkerson | 51/M | MASLD | F2 | yes | R08 a1c high |  |
| P06 | Elizabeth Adams | 44/F | MASLD | F2 | yes |  |  |
| P07 | Sandra Stewart | 43/F | MASLD | F0 | no |  |  |
| P08 | Charles Hendricks | 40/M | MASLD | F1 | yes | R10 low steps |  |
| P09 | Erik Aguilar | 39/M | MASLD | F2 | yes |  |  |
| P10 | Thomas Torres | 44/M | MASLD | F0 | yes |  | A1c 8.7% (below 9.0) |
| P11 | Allison Dixon | 55/F | MASH | F3 | no |  |  |
| P12 | Kyle Gregory | 60/M | MASH | F3 | yes | R08 a1c high |  |
| P13 | Betty Moreno | 61/F | MASH | F3 | yes |  | bilirubin 1.8x but under 2.0 mg/dL |
| P14 | Zachary Briggs | 51/M | MASH | F3 | yes | R10 low steps |  |
| P15 | Anna Gibson | 48/F | MASH | F3 | yes |  |  |
| P16 | Paul Hudson | 58/M | MASH | F3 | yes |  | steps about 2,300 a day (above 2,000) |
| P17 | Lorraine Hunter | 70/F | MASH cirrhosis | F4 | yes | R06 nsaid conflict |  |
| P18 | Brent Johnson | 52/M | MASH cirrhosis | F4 | yes | R05 platelets below 100 |  |
| P19 | William Johns | 67/M | MASH cirrhosis | F4 | yes |  | MELD 3.0 up 2 points (below 3) |
| P20 | Monica Hammond | 54/F | MASH cirrhosis | F4 | yes | R01 red flag message; R09 hcc surveillance overdue |  |
| P21 | Valerie Turner | 61/F | MASH cirrhosis | F4 | yes | R03 meld rise |  |
| P22 | Kimberly Peters | 63/F | MASH cirrhosis | F4 | yes | R05 platelets below 100; R09 hcc surveillance overdue |  |
| P23 | Amanda Cline | 58/F | MASH cirrhosis, decompensated | F4 | yes | R02 fluid gain |  |
| P24 | Brittany Mcgee | 50/F | MASH cirrhosis, decompensated | F4 | yes | R01 red flag message; R03 meld rise |  |
| P25 | Erik Moore | 69/M | MASH cirrhosis, decompensated | F4 | yes | R02 fluid gain; R04 bilirubin double |  |
| P26 | Zachary Smith | 37/M | Primary biliary cholangitis (PBC) | F2 | no |  | platelets 104 (still 100 or more) |
| P27 | Felicia Green | 53/F | Primary sclerosing cholangitis (PSC) | F2 | no |  |  |
| P28 | Henry Barton | 39/M | Autoimmune hepatitis (AIH) | F3 | yes | R07 alt double |  |
| P29 | Sarah Brown | 53/F | Alcohol-related cirrhosis | F4 | yes | R06 nsaid conflict |  |
| P30 | Bruce Wells | 65/M | MetALD (metabolic and alcohol-related liver disease) | F2 | no |  |  |

## P01 Rachel Kelley

- **Identity:** MRN LW-3684724, DOB 1994-03-08, (804) 555-0101, rachel.kelley@example.com, 797 Aaron Common Creek, Liverwell, VA 00000
- **Profile:** 32 y/o female, MASLD, fibrosis F2, health literacy high
- **Other conditions:** type 2 diabetes, sleep apnea
- **Course:** improving; 3 visits (2025-12-15 to 2026-10-16)
- **Labs, first to latest resulted:** ALT 83 to 66, AST 32 to 31, platelets 263 to 251, bilirubin 0.5 to 0.5, albumin 4.6 to 4.7, A1c 7.0 to 6.8
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 6, FIB-4 0.49
- **Held-back results (released in demo):** ALT 58, platelets 248, bilirubin 0.5, A1c 6.7, MELD 3.0 8
- **Medications:** metformin 1000 mg; semaglutide 1 mg; insulin glargine 100 units/mL
- **Allergies:** Sulfa drugs (hives)
- **Watch:** none (tests missing data)
- **Expected alerts:** none
- **Files:** notes/P01_visit1.md, notes/P01_visit2.md, notes/P01_visit3.md

## P02 Ernest Sanders

- **Identity:** MRN LW-3437069, DOB 1966-03-21, (804) 555-0102, ernest.sanders@example.com, 5681 Davis Plain Highway, Liverwell, VA 00000
- **Profile:** 60 y/o male, MASLD, fibrosis F2, health literacy average
- **Other conditions:** type 2 diabetes, hypertension, hyperlipidemia, sleep apnea
- **Course:** stable; 3 visits (2025-12-18 to 2026-10-12)
- **Labs, first to latest resulted:** ALT 69 to 58, AST 51 to 54, platelets 229 to 260, bilirubin 0.6 to 0.6, albumin 4.5 to 4.4, A1c 7.8 to 7.8
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 7, FIB-4 1.64
- **Held-back results (released in demo):** ALT 124, platelets 255, bilirubin 0.6, A1c 7.9, MELD 3.0 6
- **Medications:** metformin 1000 mg; losartan 50 mg; atorvastatin 20 mg; vitamin D3 2000 units
- **Allergies:** none
- **Watch:** 42 valid days of 42; median 11,658 steps/day; source Fitbit user 2022484408 (dates shifted)
- **Expected alerts:** none
- **Negative control:** ALT 1.8x baseline (below 2x) (must NOT alert)
- **Files:** notes/P02_visit1.md, notes/P02_visit2.md, notes/P02_visit3.md

## P03 Sarah Wood

- **Identity:** MRN LW-8177160, DOB 1980-05-17, (804) 555-0103, sarah.wood@example.com, 6169 Camacho Manors Parkways, Liverwell, VA 00000
- **Profile:** 46 y/o female, MASLD, fibrosis F2, health literacy average
- **Other conditions:** hypertension, hyperlipidemia, sleep apnea
- **Course:** worsening; 3 visits (2025-12-20 to 2026-10-22)
- **Labs, first to latest resulted:** ALT 45 to 51, AST 42 to 53, platelets 260 to 238, bilirubin 0.6 to 0.5, albumin 4.2 to 4.3, A1c 5.7 to 5.6
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 6, FIB-4 1.43
- **Held-back results (released in demo):** ALT 108, platelets 262, bilirubin 0.6, A1c 5.8, MELD 3.0 7
- **Medications:** losartan 50 mg; atorvastatin 20 mg; vitamin D3 2000 units; green tea extract supplement 500 mg
- **Allergies:** none
- **Watch:** 32 valid days of 32; median 10,113 steps/day; source Fitbit user 2347167796 (dates shifted)
- **Expected alerts:** R07_alt_double (medium, designed): ALT 45 to 108 U/L (visit 3)
- **Files:** notes/P03_visit1.md, notes/P03_visit2.md, notes/P03_visit3.md

## P04 Ryan Elliott

- **Identity:** MRN LW-5860543, DOB 1984-01-11, (804) 555-0104, ryan.elliott@example.com, 8809 Katie Viaduct Causeway, Liverwell, VA 00000
- **Profile:** 42 y/o male, MASLD, fibrosis F1, health literacy low
- **Other conditions:** type 2 diabetes, hyperlipidemia, sleep apnea
- **Course:** improving; 3 visits (2025-12-24 to 2026-10-22)
- **Labs, first to latest resulted:** ALT 46 to 47, AST 55 to 48, platelets 313 to 281, bilirubin 0.6 to 0.6, albumin 4.6 to 4.6, A1c 7.6 to 7.5
- **Scores (latest resulted):** MELD 3.0 6, MELD-Na 7, FIB-4 1.05
- **Held-back results (released in demo):** ALT 39, platelets 308, bilirubin 0.6, A1c 7.3, MELD 3.0 7
- **Medications:** metformin 1000 mg; insulin glargine 100 units/mL; atorvastatin 20 mg
- **Allergies:** Lisinopril (cough)
- **Watch:** 42 valid days of 42; median 15,903 steps/day; source Fitbit user 8877689391 (dates shifted)
- **Expected alerts:** none
- **Files:** notes/P04_visit1.md, notes/P04_visit2.md, notes/P04_visit3.md

## P05 Charles Wilkerson

- **Identity:** MRN LW-7080752, DOB 1975-08-20, (804) 555-0105, charles.wilkerson@example.com, 77848 Santiago Inlet Plaza, Liverwell, VA 00000
- **Profile:** 51 y/o male, MASLD, fibrosis F2, health literacy average
- **Other conditions:** type 2 diabetes, hypertension, hyperlipidemia
- **Course:** worsening; 3 visits (2025-12-24 to 2026-10-14)
- **Labs, first to latest resulted:** ALT 77 to 79, AST 49 to 56, platelets 270 to 299, bilirubin 0.6 to 0.7, albumin 4.7 to 4.6, A1c 7.0 to 7.1
- **Scores (latest resulted):** MELD 3.0 6, MELD-Na 6, FIB-4 1.05
- **Held-back results (released in demo):** ALT 89, platelets 301, bilirubin 0.7, A1c 9.6, MELD 3.0 7
- **Medications:** metformin 1000 mg; semaglutide 1 mg; losartan 50 mg; atorvastatin 20 mg; vitamin D3 2000 units
- **Allergies:** Codeine (nausea and vomiting)
- **Watch:** 42 valid days of 42; median 9,853 steps/day; source Fitbit user 5553957443 (dates shifted)
- **Expected alerts:** R08_a1c_high (medium, designed): A1c 9.6% (visit 3)
- **Files:** notes/P05_visit1.md, notes/P05_visit2.md, notes/P05_visit3.md

## P06 Elizabeth Adams

- **Identity:** MRN LW-7309099, DOB 1982-10-12, (804) 555-0106, elizabeth.adams@example.com, 29787 Dorsey Green Square, Liverwell, VA 00000
- **Profile:** 44 y/o female, MASLD, fibrosis F2, health literacy average
- **Other conditions:** type 2 diabetes, hypertension
- **Course:** improving; 3 visits (2025-12-21 to 2026-10-18)
- **Labs, first to latest resulted:** ALT 38 to 34, AST 46 to 39, platelets 296 to 299, bilirubin 0.6 to 0.7, albumin 4.3 to 4.4, A1c 7.2 to 6.9
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 6, FIB-4 0.96
- **Held-back results (released in demo):** ALT 27, platelets 309, bilirubin 0.7, A1c 6.4, MELD 3.0 7
- **Medications:** metformin 1000 mg; semaglutide 1 mg; losartan 50 mg; omeprazole 20 mg
- **Allergies:** Codeine (nausea and vomiting)
- **Watch:** 41 valid days of 41; median 15,484 steps/day; source Fitbit user 8053475328 (dates shifted)
- **Expected alerts:** none
- **Security test:** visit 2 note contains a hidden prompt-injection line (must be ignored)
- **Files:** notes/P06_visit1.md, notes/P06_visit2.md, notes/P06_visit3.md

## P07 Sandra Stewart

- **Identity:** MRN LW-1212691, DOB 1983-04-04, (804) 555-0107, sandra.stewart@example.com, 78472 Kirby Neck Circles, Liverwell, VA 00000
- **Profile:** 43 y/o female, MASLD, fibrosis F0, health literacy low
- **Other conditions:** hyperlipidemia, sleep apnea
- **Course:** stable; 3 visits (2025-12-19 to 2026-10-13)
- **Labs, first to latest resulted:** ALT 53 to 52, AST 46 to 44, platelets 301 to 289, bilirubin 0.8 to 0.7, albumin 4.3 to 4.2, A1c 5.2 to 5.3
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 6, FIB-4 0.91
- **Held-back results (released in demo):** ALT 54, platelets 295, bilirubin 0.8, A1c 5.5, MELD 3.0 8
- **Medications:** atorvastatin 20 mg; vitamin D3 2000 units; omeprazole 20 mg
- **Allergies:** Sulfa drugs (hives)
- **Watch:** none (tests missing data)
- **Expected alerts:** none
- **Files:** notes/P07_visit1.md, notes/P07_visit2.md, notes/P07_visit3.md

## P08 Charles Hendricks

- **Identity:** MRN LW-2552152, DOB 1986-10-05, (804) 555-0108, charles.hendricks@example.com, 07981 John River Cape, Liverwell, VA 00000
- **Profile:** 40 y/o male, MASLD, fibrosis F1, health literacy high
- **Other conditions:** hypertension, hyperlipidemia
- **Course:** worsening; 3 visits (2025-12-28 to 2026-10-21)
- **Labs, first to latest resulted:** ALT 77 to 90, AST 31 to 38, platelets 225 to 237, bilirubin 0.6 to 0.6, albumin 4.6 to 4.5, A1c 5.4 to 5.4
- **Scores (latest resulted):** MELD 3.0 6, MELD-Na 7, FIB-4 0.66
- **Held-back results (released in demo):** ALT 94, platelets 238, bilirubin 0.6, A1c 5.5, MELD 3.0 6
- **Medications:** losartan 50 mg; atorvastatin 20 mg
- **Allergies:** Penicillin (rash); Latex (itchy rash)
- **Watch:** 42 valid days of 43; median 5,289 steps/day; source Fitbit user 4319703577 (dates shifted)
- **Expected alerts:** R10_low_steps (low, designed): mean 1349 steps over 14 valid days
- **Files:** notes/P08_visit1.md, notes/P08_visit2.md, notes/P08_visit3.md

## P09 Erik Aguilar

- **Identity:** MRN LW-2212852, DOB 1987-01-14, (804) 555-0109, erik.aguilar@example.com, 2837 Susan Wells Square, Liverwell, VA 00000
- **Profile:** 39 y/o male, MASLD, fibrosis F2, health literacy average
- **Other conditions:** type 2 diabetes, hyperlipidemia
- **Course:** improving; 3 visits (2025-12-22 to 2026-10-20)
- **Labs, first to latest resulted:** ALT 81 to 74, AST 45 to 39, platelets 275 to 262, bilirubin 0.7 to 0.7, albumin 4.3 to 4.2, A1c 7.2 to 7.1
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 7, FIB-4 0.67
- **Held-back results (released in demo):** ALT 54, platelets 260, bilirubin 0.7, A1c 6.9, MELD 3.0 6
- **Medications:** metformin 1000 mg; semaglutide 1 mg; atorvastatin 20 mg; vitamin D3 2000 units
- **Allergies:** none
- **Watch:** 35 valid days of 37; median 13,041 steps/day; source Fitbit user 7007744171 (dates shifted)
- **Expected alerts:** none
- **Files:** notes/P09_visit1.md, notes/P09_visit2.md, notes/P09_visit3.md

## P10 Thomas Torres

- **Identity:** MRN LW-5242213, DOB 1982-06-27, (804) 555-0110, thomas.torres@example.com, 6283 Smith Coves Loaf, Liverwell, VA 00000
- **Profile:** 44 y/o male, MASLD, fibrosis F0, health literacy low
- **Other conditions:** hypertension, hyperlipidemia
- **Course:** stable; 3 visits (2025-12-26 to 2026-10-20)
- **Labs, first to latest resulted:** ALT 62 to 64, AST 37 to 41, platelets 223 to 247, bilirubin 0.6 to 0.6, albumin 4.5 to 4.5, A1c 5.7 to 5.7
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 7, FIB-4 0.89
- **Held-back results (released in demo):** ALT 64, platelets 239, bilirubin 0.6, A1c 8.7, MELD 3.0 7
- **Medications:** losartan 50 mg; atorvastatin 20 mg
- **Allergies:** Lisinopril (cough)
- **Watch:** 41 valid days of 41; median 11,508 steps/day; source Fitbit user 3977333714 (dates shifted)
- **Expected alerts:** none
- **Negative control:** A1c 8.7% (below 9.0) (must NOT alert)
- **Files:** notes/P10_visit1.md, notes/P10_visit2.md, notes/P10_visit3.md

## P11 Allison Dixon

- **Identity:** MRN LW-3823000, DOB 1971-09-27, (804) 555-0111, allison.dixon@example.com, 4751 Rush Ports River, Liverwell, VA 00000
- **Profile:** 55 y/o female, MASH, fibrosis F3, health literacy low
- **Other conditions:** type 2 diabetes
- **Course:** improving; 3 visits (2025-12-25 to 2026-10-17)
- **Labs, first to latest resulted:** ALT 105 to 64, AST 56 to 48, platelets 214 to 207, bilirubin 0.7 to 0.7, albumin 4.4 to 4.4, A1c 7.1 to 6.9
- **Scores (latest resulted):** MELD 3.0 8, MELD-Na 7, FIB-4 1.57
- **Held-back results (released in demo):** ALT 76, platelets 206, bilirubin 0.8, A1c 6.5, MELD 3.0 7
- **Medications:** metformin 1000 mg; vitamin D3 2000 units
- **Allergies:** Lisinopril (cough); Penicillin (rash)
- **Watch:** none (tests missing data)
- **Expected alerts:** none
- **Files:** notes/P11_visit1.md, notes/P11_visit2.md, notes/P11_visit3.md

## P12 Kyle Gregory

- **Identity:** MRN LW-9462969, DOB 1966-07-25, (804) 555-0112, kyle.gregory@example.com, 86032 Deborah Villages Causeway, Liverwell, VA 00000
- **Profile:** 60 y/o male, MASH, fibrosis F3, health literacy average
- **Other conditions:** type 2 diabetes, sleep apnea
- **Course:** stable; 3 visits (2025-12-26 to 2026-10-21)
- **Labs, first to latest resulted:** ALT 92 to 94, AST 47 to 49, platelets 180 to 176, bilirubin 0.8 to 0.9, albumin 4.2 to 4.0, A1c 7.5 to 7.4
- **Scores (latest resulted):** MELD 3.0 6, MELD-Na 6, FIB-4 1.69
- **Held-back results (released in demo):** ALT 91, platelets 178, bilirubin 0.8, A1c 9.4, MELD 3.0 6
- **Medications:** metformin 1000 mg; semaglutide 1 mg; insulin glargine 100 units/mL
- **Allergies:** Lisinopril (cough)
- **Watch:** 44 valid days of 44; median 11,083 steps/day; source Fitbit user 6962181067 (dates shifted)
- **Expected alerts:** R08_a1c_high (medium, designed): A1c 9.4% (visit 3)
- **Files:** notes/P12_visit1.md, notes/P12_visit2.md, notes/P12_visit3.md

## P13 Betty Moreno

- **Identity:** MRN LW-4309114, DOB 1965-02-18, (804) 555-0113, betty.moreno@example.com, 222 Nelson Place Mall, Liverwell, VA 00000
- **Profile:** 61 y/o female, MASH, fibrosis F3, health literacy low
- **Other conditions:** type 2 diabetes, hypertension, sleep apnea
- **Course:** stable; 3 visits (2025-12-28 to 2026-10-22)
- **Labs, first to latest resulted:** ALT 72 to 65, AST 82 to 81, platelets 168 to 156, bilirubin 0.6 to 0.8, albumin 4.2 to 4.2, A1c 6.6 to 6.7
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 6, FIB-4 3.93
- **Held-back results (released in demo):** ALT 67, platelets 160, bilirubin 1.1, A1c 6.7, MELD 3.0 8
- **Medications:** metformin 1000 mg; losartan 50 mg
- **Allergies:** none
- **Watch:** 30 valid days of 39; median 10,249 steps/day; source Fitbit user 4388161847 (dates shifted)
- **Expected alerts:** none
- **Negative control:** bilirubin 1.8x but under 2.0 mg/dL (must NOT alert)
- **Files:** notes/P13_visit1.md, notes/P13_visit2.md, notes/P13_visit3.md

## P14 Zachary Briggs

- **Identity:** MRN LW-8792279, DOB 1975-06-19, (804) 555-0114, zachary.briggs@example.com, 7258 Wallace Pine Underpass, Liverwell, VA 00000
- **Profile:** 51 y/o male, MASH, fibrosis F3, health literacy high
- **Other conditions:** type 2 diabetes, hypertension
- **Course:** worsening; 3 visits (2025-12-24 to 2026-10-20)
- **Labs, first to latest resulted:** ALT 100 to 116, AST 63 to 87, platelets 200 to 209, bilirubin 0.7 to 0.8, albumin 4.1 to 3.9, A1c 6.8 to 7.1
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 7, FIB-4 1.93
- **Held-back results (released in demo):** ALT 138, platelets 187, bilirubin 0.7, A1c 7.1, MELD 3.0 7
- **Medications:** metformin 1000 mg; semaglutide 1 mg; losartan 50 mg
- **Allergies:** Latex (itchy rash)
- **Watch:** 41 valid days of 42; median 5,813 steps/day; source Fitbit user 7086361926 (dates shifted)
- **Expected alerts:** R10_low_steps (low, designed): mean 1256 steps over 14 valid days
- **Files:** notes/P14_visit1.md, notes/P14_visit2.md, notes/P14_visit3.md

## P15 Anna Gibson

- **Identity:** MRN LW-2870694, DOB 1978-07-31, (804) 555-0115, anna.gibson@example.com, 6820 Bradford Knoll Points, Liverwell, VA 00000
- **Profile:** 48 y/o female, MASH, fibrosis F3, health literacy average
- **Other conditions:** type 2 diabetes, hyperlipidemia, sleep apnea
- **Course:** improving; 3 visits (2025-12-15 to 2026-10-16)
- **Labs, first to latest resulted:** ALT 55 to 41, AST 63 to 52, platelets 171 to 175, bilirubin 0.6 to 0.6, albumin 4.1 to 4.2, A1c 8.0 to 7.5
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 6, FIB-4 2.18
- **Held-back results (released in demo):** ALT 37, platelets 177, bilirubin 0.6, A1c 7.3, MELD 3.0 7
- **Medications:** metformin 1000 mg; semaglutide 1 mg; atorvastatin 20 mg
- **Allergies:** none
- **Watch:** 48 valid days of 49; median 12,231 steps/day; source Fitbit user 1503960366 (dates shifted)
- **Expected alerts:** none
- **Security test:** visit 1 note contains a hidden prompt-injection line (must be ignored)
- **Files:** notes/P15_visit1.md, notes/P15_visit2.md, notes/P15_visit3.md

## P16 Paul Hudson

- **Identity:** MRN LW-2200634, DOB 1968-10-15, (804) 555-0116, paul.hudson@example.com, 482 Kimberly Court Mews, Liverwell, VA 00000
- **Profile:** 58 y/o male, MASH, fibrosis F3, health literacy high
- **Other conditions:** type 2 diabetes, hyperlipidemia
- **Course:** stable; 3 visits (2025-12-17 to 2026-10-17)
- **Labs, first to latest resulted:** ALT 57 to 59, AST 87 to 75, platelets 185 to 179, bilirubin 0.6 to 0.6, albumin 4.1 to 4.2, A1c 7.4 to 7.3
- **Scores (latest resulted):** MELD 3.0 6, MELD-Na 6, FIB-4 3.11
- **Held-back results (released in demo):** ALT 55, platelets 181, bilirubin 0.5, A1c 7.3, MELD 3.0 6
- **Medications:** metformin 1000 mg; insulin glargine 100 units/mL; atorvastatin 20 mg
- **Allergies:** Codeine (nausea and vomiting)
- **Watch:** 42 valid days of 42; median 6,534 steps/day; source Fitbit user 8378563200 (dates shifted)
- **Expected alerts:** none
- **Negative control:** steps about 2,300 a day (above 2,000) (must NOT alert)
- **Files:** notes/P16_visit1.md, notes/P16_visit2.md, notes/P16_visit3.md

## P17 Lorraine Hunter

- **Identity:** MRN LW-7695457, DOB 1956-03-12, (804) 555-0117, lorraine.hunter@example.com, 9145 Jose Circles Bridge, Liverwell, VA 00000
- **Profile:** 70 y/o female, MASH cirrhosis, fibrosis F4, health literacy average
- **Other conditions:** type 2 diabetes, hypertension, hyperlipidemia
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-24 to 2026-10-23)
- **Labs, first to latest resulted:** ALT 44 to 43, AST 39 to 37, platelets 130 to 149, bilirubin 0.9 to 0.9, albumin 3.8 to 3.2, A1c 7.2 to 7.2
- **Scores (latest resulted):** MELD 3.0 9, MELD-Na 8, FIB-4 2.65
- **Held-back results (released in demo):** ALT 48, platelets 127, bilirubin 1.0, A1c 7.2, MELD 3.0 9
- **Medications:** metformin 1000 mg; semaglutide 1 mg; losartan 50 mg; atorvastatin 20 mg; investigational study drug LW-101 or placebo (fictional study) 1 mL; ibuprofen 400 mg
- **Allergies:** Lisinopril (cough)
- **Watch:** 31 valid days of 38; median 8,915 steps/day; source Fitbit user 6117666160 (dates shifted)
- **Expected alerts:** R06_nsaid_conflict (medium, designed): ibuprofen active while plan says No NSAIDs
- **Files:** notes/P17_visit1.md, notes/P17_visit2.md, notes/P17_visit3.md, notes/P17_visit4.md

## P18 Brent Johnson

- **Identity:** MRN LW-8859515, DOB 1974-04-28, (804) 555-0118, brent.johnson@example.com, 18955 Lawson Shoal Station, Liverwell, VA 00000
- **Profile:** 52 y/o male, MASH cirrhosis, fibrosis F4, health literacy low
- **Other conditions:** type 2 diabetes, hypertension
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-26 to 2026-10-21)
- **Labs, first to latest resulted:** ALT 55 to 56, AST 65 to 74, platelets 112 to 112, bilirubin 1.4 to 1.0, albumin 4.0 to 4.4, A1c 6.8 to 6.8
- **Scores (latest resulted):** MELD 3.0 8, MELD-Na 9, FIB-4 4.59
- **Held-back results (released in demo):** ALT 58, platelets 87, bilirubin 1.1, A1c 7.0, MELD 3.0 8
- **Medications:** metformin 1000 mg; insulin glargine 100 units/mL; losartan 50 mg; investigational study drug LW-101 or placebo (fictional study) 1 mL; acetaminophen 500 mg
- **Allergies:** Latex (itchy rash)
- **Watch:** 39 valid days of 41; median 8,869 steps/day; source Fitbit user 5577150313 (dates shifted)
- **Expected alerts:** R05_platelets_below_100 (medium, designed): platelets 112 to 87 (visit 4)
- **Files:** notes/P18_visit1.md, notes/P18_visit2.md, notes/P18_visit3.md, notes/P18_visit4.md

## P19 William Johns

- **Identity:** MRN LW-7294265, DOB 1959-01-20, (804) 555-0119, william.johns@example.com, 584 Carter Viaduct Knolls, Liverwell, VA 00000
- **Profile:** 67 y/o male, MASH cirrhosis, fibrosis F4, health literacy low
- **Other conditions:** hyperlipidemia
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-16 to 2026-10-20)
- **Labs, first to latest resulted:** ALT 43 to 36, AST 76 to 70, platelets 129 to 119, bilirubin 1.3 to 0.9, albumin 3.8 to 3.8, A1c 5.9 to 5.8
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 7, FIB-4 6.57
- **Held-back results (released in demo):** ALT 42, platelets 128, bilirubin 1.2, A1c 5.7, MELD 3.0 9
- **Medications:** atorvastatin 20 mg; omeprazole 20 mg; acetaminophen 500 mg
- **Allergies:** none
- **Watch:** 44 valid days of 45; median 8,172 steps/day; source Fitbit user 4702921684 (dates shifted)
- **Expected alerts:** none
- **Negative control:** MELD 3.0 up 2 points (below 3) (must NOT alert)
- **Files:** notes/P19_visit1.md, notes/P19_visit2.md, notes/P19_visit3.md, notes/P19_visit4.md

## P20 Monica Hammond

- **Identity:** MRN LW-9317974, DOB 1972-07-16, (804) 555-0120, monica.hammond@example.com, 46590 Gonzalez Centers Stravenue, Liverwell, VA 00000
- **Profile:** 54 y/o female, MASH cirrhosis, fibrosis F4, health literacy average
- **Other conditions:** type 2 diabetes, hypertension, hyperlipidemia
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-22 to 2026-10-18)
- **Labs, first to latest resulted:** ALT 64 to 64, AST 71 to 84, platelets 123 to 106, bilirubin 1.3 to 1.5, albumin 4.1 to 4.2, A1c 6.5 to 6.7
- **Scores (latest resulted):** MELD 3.0 10, MELD-Na 9, FIB-4 5.35
- **Held-back results (released in demo):** ALT 70, platelets 121, bilirubin 1.4, A1c 6.7, MELD 3.0 10
- **Medications:** metformin 1000 mg; losartan 50 mg; atorvastatin 20 mg; carvedilol 6.25 mg; vitamin D3 2000 units; acetaminophen 500 mg
- **Allergies:** Lisinopril (cough); Penicillin (rash)
- **Watch:** 42 valid days of 42; median 7,683 steps/day; source Fitbit user 2873212765 (dates shifted)
- **Expected alerts:** R01_red_flag_message (urgent, designed): message mentions: like tar; R09_hcc_surveillance_overdue (low, designed): last ultrasound 2026-03-05 (235 days ago)
- **Files:** notes/P20_visit1.md, notes/P20_visit2.md, notes/P20_visit3.md, notes/P20_visit4.md

## P21 Valerie Turner

- **Identity:** MRN LW-5958202, DOB 1965-07-05, (804) 555-0121, valerie.turner@example.com, 9256 Bennett Trail Manor, Liverwell, VA 00000
- **Profile:** 61 y/o female, MASH cirrhosis, fibrosis F4, health literacy high
- **Other conditions:** type 2 diabetes, hyperlipidemia
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-18 to 2026-10-21)
- **Labs, first to latest resulted:** ALT 30 to 30, AST 64 to 69, platelets 126 to 107, bilirubin 0.9 to 0.7, albumin 4.0 to 4.0, A1c 7.6 to 7.7
- **Scores (latest resulted):** MELD 3.0 9, MELD-Na 8, FIB-4 7.18
- **Held-back results (released in demo):** ALT 28, platelets 120, bilirubin 1.0, A1c 7.7, MELD 3.0 12
- **Medications:** metformin 1000 mg; atorvastatin 20 mg; acetaminophen 500 mg
- **Allergies:** none
- **Watch:** 40 valid days of 40; median 7,487 steps/day; source Fitbit user 1644430081 (dates shifted)
- **Expected alerts:** R03_meld_rise (high, designed): MELD 3.0 9 to 12 (visit 4)
- **Files:** notes/P21_visit1.md, notes/P21_visit2.md, notes/P21_visit3.md, notes/P21_visit4.md

## P22 Kimberly Peters

- **Identity:** MRN LW-3499526, DOB 1963-06-15, (804) 555-0122, kimberly.peters@example.com, 2300 Weaver Mall Greens, Liverwell, VA 00000
- **Profile:** 63 y/o female, MASH cirrhosis, fibrosis F4, health literacy high
- **Other conditions:** type 2 diabetes, hypertension
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-18 to 2026-10-13)
- **Labs, first to latest resulted:** ALT 46 to 48, AST 43 to 43, platelets 131 to 111, bilirubin 0.9 to 1.0, albumin 3.8 to 3.6, A1c 7.5 to 7.6
- **Scores (latest resulted):** MELD 3.0 8, MELD-Na 8, FIB-4 3.52
- **Held-back results (released in demo):** ALT 56, platelets 92, bilirubin 1.2, A1c 7.9, MELD 3.0 10
- **Medications:** metformin 1000 mg; semaglutide 1 mg; insulin glargine 100 units/mL; losartan 50 mg; acetaminophen 500 mg
- **Allergies:** Penicillin (rash); Latex (itchy rash)
- **Watch:** 42 valid days of 42; median 7,089 steps/day; source Fitbit user 4558609924 (dates shifted)
- **Expected alerts:** R05_platelets_below_100 (medium, designed): platelets 111 to 92 (visit 4); R09_hcc_surveillance_overdue (low, designed): last ultrasound 2026-02-21 (247 days ago)
- **Files:** notes/P22_visit1.md, notes/P22_visit2.md, notes/P22_visit3.md, notes/P22_visit4.md

## P23 Amanda Cline

- **Identity:** MRN LW-1252769, DOB 1968-10-17, (804) 555-0123, amanda.cline@example.com, 458 Brown Ville Branch, Liverwell, VA 00000
- **Profile:** 58 y/o female, MASH cirrhosis, decompensated, fibrosis F4, health literacy high
- **Other conditions:** hypertension, ascites
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-15 to 2026-10-12)
- **Labs, first to latest resulted:** ALT 28 to 31, AST 49 to 48, platelets 130 to 106, bilirubin 2.2 to 2.8, albumin 3.0 to 3.1, A1c 5.5 to 5.5
- **Scores (latest resulted):** MELD 3.0 19, MELD-Na 18, FIB-4 4.64
- **Held-back results (released in demo):** ALT 31, platelets 110, bilirubin 2.8, A1c 5.6, MELD 3.0 20
- **Medications:** carvedilol 6.25 mg; furosemide 40 mg; spironolactone 100 mg
- **Allergies:** Codeine (nausea and vomiting); Penicillin (rash)
- **Watch:** 30 valid days of 30; median 6,764 steps/day; source Fitbit user 3372868164 (dates shifted)
- **Expected alerts:** R02_fluid_gain (high, designed): weight 81.6 kg vs 79.6 kg about 7 days earlier
- **Files:** notes/P23_visit1.md, notes/P23_visit2.md, notes/P23_visit3.md, notes/P23_visit4.md

## P24 Brittany Mcgee

- **Identity:** MRN LW-4606146, DOB 1975-11-28, (804) 555-0124, brittany.mcgee@example.com, 5384 Callahan Landing Knolls, Liverwell, VA 00000
- **Profile:** 50 y/o female, MASH cirrhosis, decompensated, fibrosis F4, health literacy high
- **Other conditions:** hypertension, ascites, h/o HE
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-16 to 2026-10-16)
- **Labs, first to latest resulted:** ALT 38 to 39, AST 59 to 56, platelets 134 to 155, bilirubin 1.7 to 1.7, albumin 3.0 to 2.6, A1c 5.9 to 5.8
- **Scores (latest resulted):** MELD 3.0 18, MELD-Na 17, FIB-4 2.89
- **Held-back results (released in demo):** ALT 35, platelets 141, bilirubin 2.5, A1c 5.7, MELD 3.0 21
- **Medications:** carvedilol 6.25 mg; furosemide 40 mg; spironolactone 100 mg; lactulose 20 g/30 mL; rifaximin 550 mg; vitamin D3 2000 units; omeprazole 20 mg; acetaminophen 500 mg
- **Allergies:** Latex (itchy rash)
- **Watch:** 26 valid days of 39; median 6,688 steps/day; source Fitbit user 6290855005 (dates shifted)
- **Expected alerts:** R01_red_flag_message (urgent, designed): message mentions: coffee grounds; R03_meld_rise (high, designed): MELD 3.0 18 to 21 (visit 4)
- **Files:** notes/P24_visit1.md, notes/P24_visit2.md, notes/P24_visit3.md, notes/P24_visit4.md

## P25 Erik Moore

- **Identity:** MRN LW-2838600, DOB 1957-04-25, (804) 555-0125, erik.moore@example.com, 2705 Pope Route Extensions, Liverwell, VA 00000
- **Profile:** 69 y/o male, MASH cirrhosis, decompensated, fibrosis F4, health literacy average
- **Other conditions:** ascites
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-17 to 2026-10-18)
- **Labs, first to latest resulted:** ALT 39 to 44, AST 52 to 47, platelets 131 to 117, bilirubin 1.8 to 1.6, albumin 3.4 to 3.4, A1c 5.6 to 5.6
- **Scores (latest resulted):** MELD 3.0 14, MELD-Na 15, FIB-4 4.18
- **Held-back results (released in demo):** ALT 42, platelets 120, bilirubin 3.8, A1c 5.8, MELD 3.0 17
- **Medications:** carvedilol 6.25 mg; furosemide 40 mg; spironolactone 100 mg; acetaminophen 500 mg
- **Allergies:** Sulfa drugs (hives); Penicillin (rash)
- **Watch:** 33 valid days of 39; median 5,843 steps/day; source Fitbit user 8583815059 (dates shifted)
- **Expected alerts:** R02_fluid_gain (high, designed): weight 94.5 kg vs 92.0 kg about 7 days earlier; R03_meld_rise (high, natural): MELD 3.0 14 to 17 (visit 4); R04_bilirubin_double (high, designed): bilirubin 1.8 to 3.8 mg/dL (visit 4)
- **Files:** notes/P25_visit1.md, notes/P25_visit2.md, notes/P25_visit3.md, notes/P25_visit4.md

## P26 Zachary Smith

- **Identity:** MRN LW-7635748, DOB 1989-04-12, (804) 555-0126, zachary.smith@example.com, 94906 Ryan Path Valleys, Liverwell, VA 00000
- **Profile:** 37 y/o male, Primary biliary cholangitis (PBC), fibrosis F2, health literacy average
- **Other conditions:** none
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-11 to 2026-10-15)
- **Labs, first to latest resulted:** ALT 58 to 62, AST 51 to 60, platelets 154 to 115, bilirubin 0.9 to 0.8, albumin 4.3 to 4.0, A1c 5.7 to 5.9
- **Scores (latest resulted):** MELD 3.0 6, MELD-Na 6, FIB-4 2.45
- **Held-back results (released in demo):** ALT 70, platelets 104, bilirubin 1.0, A1c 5.9, MELD 3.0 6
- **Medications:** ursodiol 500 mg
- **Allergies:** none
- **Watch:** none (tests missing data)
- **Expected alerts:** none
- **Negative control:** platelets 104 (still 100 or more) (must NOT alert)
- **Files:** notes/P26_visit1.md, notes/P26_visit2.md, notes/P26_visit3.md, notes/P26_visit4.md

## P27 Felicia Green

- **Identity:** MRN LW-4983839, DOB 1973-03-17, (804) 555-0127, felicia.green@example.com, 93244 Howard Loaf Field, Liverwell, VA 00000
- **Profile:** 53 y/o female, Primary sclerosing cholangitis (PSC), fibrosis F2, health literacy low
- **Other conditions:** none
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-22 to 2026-10-23)
- **Labs, first to latest resulted:** ALT 92 to 97, AST 53 to 48, platelets 230 to 188, bilirubin 0.6 to 0.4, albumin 4.7 to 4.5, A1c 5.5 to 5.4
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 6, FIB-4 1.37
- **Held-back results (released in demo):** ALT 88, platelets 167, bilirubin 0.4, A1c 5.4, MELD 3.0 7
- **Medications:** 
- **Allergies:** Lisinopril (cough)
- **Watch:** none (tests missing data)
- **Expected alerts:** none
- **Files:** notes/P27_visit1.md, notes/P27_visit2.md, notes/P27_visit3.md, notes/P27_visit4.md

## P28 Henry Barton

- **Identity:** MRN LW-5698828, DOB 1986-12-08, (804) 555-0128, henry.barton@example.com, 280 Leonard Drive Estates, Liverwell, VA 00000
- **Profile:** 39 y/o male, Autoimmune hepatitis (AIH), fibrosis F3, health literacy high
- **Other conditions:** none
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-22 to 2026-10-17)
- **Labs, first to latest resulted:** ALT 96 to 91, AST 72 to 72, platelets 282 to 264, bilirubin 0.6 to 0.5, albumin 4.8 to 4.2, A1c 5.5 to 5.6
- **Scores (latest resulted):** MELD 3.0 7, MELD-Na 8, FIB-4 1.11
- **Held-back results (released in demo):** ALT 230, platelets 260, bilirubin 0.6, A1c 5.8, MELD 3.0 7
- **Medications:** prednisone 10 mg; azathioprine 50 mg; vitamin D3 2000 units
- **Allergies:** Sulfa drugs (hives); Latex (itchy rash)
- **Watch:** 38 valid days of 62; median 5,375 steps/day; source Fitbit user 4020332650 (dates shifted)
- **Expected alerts:** R07_alt_double (medium, designed): ALT 96 to 230 U/L (visit 4)
- **Files:** notes/P28_visit1.md, notes/P28_visit2.md, notes/P28_visit3.md, notes/P28_visit4.md

## P29 Sarah Brown

- **Identity:** MRN LW-3028626, DOB 1973-06-29, (804) 555-0129, sarah.brown@example.com, 3829 David Islands Oval, Liverwell, VA 00000
- **Profile:** 53 y/o female, Alcohol-related cirrhosis, fibrosis F4, health literacy low
- **Other conditions:** hypertension
- **Course:** cirrhosis trend (Mayo pattern); 4 visits (2026-01-09 to 2026-10-14)
- **Labs, first to latest resulted:** ALT 40 to 38, AST 82 to 72, platelets 121 to 121, bilirubin 1.3 to 1.0, albumin 3.9 to 3.6, A1c 5.4 to 5.4
- **Scores (latest resulted):** MELD 3.0 8, MELD-Na 8, FIB-4 5.12
- **Held-back results (released in demo):** ALT 39, platelets 117, bilirubin 1.4, A1c 5.6, MELD 3.0 10
- **Medications:** losartan 50 mg; carvedilol 6.25 mg; acetaminophen 500 mg; naproxen 220 mg
- **Allergies:** none
- **Watch:** 38 valid days of 42; median 4,904 steps/day; source Fitbit user 2320127002 (dates shifted)
- **Expected alerts:** R06_nsaid_conflict (medium, designed): naproxen active while plan says No NSAIDs
- **Files:** notes/P29_visit1.md, notes/P29_visit2.md, notes/P29_visit3.md, notes/P29_visit4.md

## P30 Bruce Wells

- **Identity:** MRN LW-3881079, DOB 1961-01-29, (804) 555-0130, bruce.wells@example.com, 1883 Sutton Motorway Prairie, Liverwell, VA 00000
- **Profile:** 65 y/o male, MetALD (metabolic and alcohol-related liver disease), fibrosis F2, health literacy average
- **Other conditions:** hypertension
- **Course:** stable; 3 visits (2025-12-23 to 2026-10-23)
- **Labs, first to latest resulted:** ALT 41 to 41, AST 62 to 67, platelets 283 to 263, bilirubin 0.9 to 0.9, albumin 4.5 to 4.9, A1c 5.5 to 5.6
- **Scores (latest resulted):** MELD 3.0 6, MELD-Na 6, FIB-4 2.59
- **Held-back results (released in demo):** ALT 37, platelets 274, bilirubin 0.9, A1c 5.6, MELD 3.0 6
- **Medications:** losartan 50 mg; vitamin D3 2000 units
- **Allergies:** none
- **Watch:** none (tests missing data)
- **Expected alerts:** none
- **Files:** notes/P30_visit1.md, notes/P30_visit2.md, notes/P30_visit3.md
