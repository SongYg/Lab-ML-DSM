0:Row
1:Sample Name
2:Transaction Id
3:Anon Student Id
4:Session Id
5:Time
6:Time Zone
7:Duration (sec)
8:Student Response Type
9:Student Response Subtype
10:Tutor Response Type
11:Tutor Response Subtype
12:Level (Sequence)
13:Level (Unit)
14:Level (Module)
15:Level (Section1)
16:Problem Name
17:Problem View
18:Problem Start Time
19:Step Name
20:Attempt At Step
21:Is Last Attempt
22:Outcome
23:Selection
24:Action
25:Input
26:Feedback Text
27:Feedback Classification
28:Help Level
29:Total Num Hints
30:KC (Single-KC)
31:KC Category (Single-KC)
32:KC (Unique-step)
33:KC Category (Unique-step)
34:KC (Model1)
35:KC Category (Model1)
36:KC (Model2)
37:KC Category (Model2)
38:KC (Model3)
39:KC Category (Model3)
40:KC (Model4)
41:KC Category (Model4)
42:KC (intro_biology-1.0)
43:KC Category (intro_biology-1.0)
44:KC (intro_biology-1.0)
45:KC Category (intro_biology-1.0)
46:KC (intro_biology-1.0)
47:KC Category (intro_biology-1.0)
48:KC (intro_biology-1.0)
49:KC Category (intro_biology-1.0)
50:KC (intro_biology-1.0)
51:KC Category (intro_biology-1.0)
52:KC (intro_biology-1.0)
53:KC Category (intro_biology-1.0)
54:KC (intro_biology-1.0)
55:KC Category (intro_biology-1.0)
56:KC (intro_biology-1.0)
57:KC Category (intro_biology-1.0)
58:KC (intro_biology-1.0)
59:KC Category (intro_biology-1.0)
60:KC (intro_biology-1.0)
61:KC Category (intro_biology-1.0)
62:KC (intro_biology-1.0)
63:KC Category (intro_biology-1.0)
64:KC (intro_biology-1.0)
65:KC Category (intro_biology-1.0)
66:KC (intro_biology-1.0)
67:KC Category (intro_biology-1.0)
68:KC (intro_biology-1.0)
69:KC Category (intro_biology-1.0)
70:KC (intro_biology-1.0)
71:KC Category (intro_biology-1.0)
72:KC (intro_biology-1.0)
73:KC Category (intro_biology-1.0)
74:KC (intro_biology-1.0)
75:KC Category (intro_biology-1.0)
76:KC (intro_biology-1.0)
77:KC Category (intro_biology-1.0)
78:KC (intro_biology-1.0)
79:KC Category (intro_biology-1.0)
80:KC (intro_biology-1.0)
81:KC Category (intro_biology-1.0)
82:KC (intro_biology-1.0)
83:KC Category (intro_biology-1.0)
84:KC (intro_biology-1.0)
85:KC Category (intro_biology-1.0)
86:KC (intro_biology-1.0)
87:KC Category (intro_biology-1.0)
88:KC (intro_biology-1.0)
89:KC Category (intro_biology-1.0)
90:KC (intro_biology-1.0)
91:KC Category (intro_biology-1.0)
92:KC (intro_biology-1.0)
93:KC Category (intro_biology-1.0)
94:KC (intro_biology-1.0)
95:KC Category (intro_biology-1.0)
96:KC (intro_biology-1.0)
97:KC Category (intro_biology-1.0)
98:KC (intro_biology-1.0)
99:KC Category (intro_biology-1.0)
100:KC (intro_biology-1.0)
101:KC Category (intro_biology-1.0)
102:KC (Model1_clst100_nm_nmfC20)
103:KC Category (Model1_clst100_nm_nmfC20)
104:KC (Model1_clst100w_nm_nmfC10old)
105:KC Category (Model1_clst100w_nm_nmfC10old)
106:KC (Model1_clst100w_nm_nmfC10old)
107:KC Category (Model1_clst100w_nm_nmfC10old)
108:KC (Model1_clst75_nm_nmfC10old)
109:KC Category (Model1_clst75_nm_nmfC10old)
110:KC (Model1_clst75_nm_nmfC10)
111:KC Category (Model1_clst75_nm_nmfC10)
112:KC (paa-flip_nt1-lo05-d100)
113:KC Category (paa-flip_nt1-lo05-d100)
114:KC (paa-flip_nt1-lo05-d100)
115:KC Category (paa-flip_nt1-lo05-d100)
116:KC (paa-flip_nt1-lo05-d100)
117:KC Category (paa-flip_nt1-lo05-d100)
118:KC (paa-flip_nt1-lo05-d100)
119:KC Category (paa-flip_nt1-lo05-d100)
120:KC (paa-flip_nt1-lo05-d100)
121:KC Category (paa-flip_nt1-lo05-d100)
122:KC (paa-flip_nt1-lo05-d100)
123:KC Category (paa-flip_nt1-lo05-d100)
124:KC (Item Model)
125:KC Category (Item Model)
126:KC (Paragraph Based 16 clusters)
127:KC Category (Paragraph Based 16 clusters)
128:KC (Paragraph Based 21 clusters)
129:KC Category (Paragraph Based 21 clusters)
130:School
131:Class
132:CF (oli:activityGuid)
133:CF (oli:highStakes)
134:CF (oli:purpose)
135:CF (oli:resourceType)

mysql> show tables;
+----------------------------+
| Tables_in_dsmdb            |
+----------------------------+
| DSM_feedback               |
| DSM_hint                   |
| DSM_module                 |
| DSM_problem                |
| DSM_section                |
| DSM_sequence               |
| DSM_step                   |
| DSM_student                |
| DSM_unit                   |
| auth_group                 |
| auth_group_permissions     |
| auth_permission            |
| auth_user                  |
| auth_user_groups           |
| auth_user_user_permissions |
| django_admin_log           |
| django_content_type        |
| django_migrations          |
| django_session             |
+----------------------------+


create view hierarchy as select DSM_step.step_name, DSM_step.step_id, DSM_problem.problem_name, DSM_problem.problem_id, DSM_module.module_name, DSM_module.module_id, DSM_unit.unit_name, DSM_unit.unit_id, DSM_sequence.sequence_id, DSM_sequence.sequence_name from DSM_step inner join DSM_problem on DSM_step.problem_id = DSM_problem.problem_id inner join DSM_module on DSM_problem.module_id = DSM_module.module_id inner join DSM_unit on DSM_module.unit_id = DSM_unit.unit_id inner join DSM_sequence on DSM_unit.sequence_id = DSM_sequence.sequence_id;

1   All Data    65de9c1cd951cbacffda88ddb02b4e3f    Stu_0059b4a35882a65132c467536b41975c    2ea7b86b0a1dac302935d2bcd1d0ef84    2014-04-04 17:32:24 America/New_York    0   VIEW_PAGE   UI Event            Introduction to Biology Introduction to Chemistry   Chemical Bonds      biochem_bonding_quiz    1   2014-04-04 17:32:24                 Navigation  SelectPageNumber    1                                                                                                                                                                                                                                                                                                                                                                                                                                   UC Davis    bisa2014                
