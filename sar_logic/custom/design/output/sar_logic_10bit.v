
module sar_logic (   clock,
  reset_n,
  cmp_p,
  cmp_n,
  clk_sample,
  clkc,
  result,
  switch_p,
  switch_n,
  switch_bp,
  switch_bn,
  switch_refp_l,
  switch_refp_r,
  switch_refn_l,
  switch_refn_r,
  clock_output );

  input clock;
  input reset_n;
  input cmp_p;
  input cmp_n;
  output clk_sample;
  output clkc;
  output [10:0] result;
  output [9:0] switch_p;
  output [9:0] switch_n;
  output [9:0] switch_bp;
  output [9:0] switch_bn;
  output [9:0] switch_refp_l;
  output [9:0] switch_refp_r;
  output [9:0] switch_refn_l;
  output [9:0] switch_refn_r;
  output clock_output;
  wire QB;
  wire [12:1] Q;
  wire [9:0] refp;
  wire [9:0] refn;
  wire [10:0] N;
  wire [10:0] P;
  wire [10:1] N_B;
  wire [10:1] P_B;
  wire [10:1] N_Q;
  wire [10:1] N_QB;
  wire [10:1] P_Q;
  wire [10:1] P_QB;
  dff1BWP I0 (   .Q (Q[1]),   .QN (QB),   .CDN (INT_RST),   .CP (RDY),   .D (Q[2]) );
  dffq1BWP I1 (   .Q (N[0]),   .CDN (INT_RST),   .CP (Q[1]),   .D (OUTM) );
  dffq1BWP I2 (   .Q (P[0]),   .CDN (INT_RST),   .CP (Q[1]),   .D (OUTP) );
  in2BWP I3 (   .ZN (clock_output),   .I (net039) );
  dffq1BWP I4 (   .Q (INT_RST),   .CDN (reset_n),   .CP (SYS_CLKB),   .D (QB) );
  dff1BWP I5 (   .Q (Q[12]),   .QN (QB_12),   .CDN (INT_RST),   .CP (clock),   .D (high_net) );
  in2BWP I6 (   .ZN (clk_sample_b),   .I (QB_12) );
  tiehBWP I7 (   .Z (high_net) );
  in0BWP I8 (   .ZN (SYS_CLKB),   .I (clock) );
  nand20BWP I9 (   .ZN (OUTP_I),   .A1 (cmp_p),   .A2 (OUTM_I) );
  nand20BWP I10 (   .ZN (OUTM_I),   .A1 (OUTP_I),   .A2 (cmp_n) );
  buff2BWP I11 (   .Z (OUTP),   .I (OUTP_I) );
  buff2BWP I12 (   .Z (OUTM),   .I (OUTM_I) );
  nor20BWP I13 (   .ZN (net039),   .A1 (P[0]),   .A2 (N[0]) );
  in4BWP I14 (   .ZN (RDY),   .I (net08) );
  nor20BWP I15 (   .ZN (net010),   .A1 (cmp_p),   .A2 (cmp_n) );
  delay251BWP I16 (   .Z (net08),   .I (net010) );
  dffq1BWP I17 (   .Q (Q[2]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[3]) );
  dff1BWP I18 (   .Q (N_Q[1]),   .QN (N_QB[1]),   .CDN (INT_RST),   .CP (Q[2]),   .D (OUTM) );
  dff1BWP I19 (   .Q (P_Q[1]),   .QN (P_QB[1]),   .CDN (INT_RST),   .CP (Q[2]),   .D (OUTP) );
  dffq1BWP I20 (   .Q (Q[3]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[4]) );
  dff1BWP I21 (   .Q (N_Q[2]),   .QN (N_QB[2]),   .CDN (INT_RST),   .CP (Q[3]),   .D (OUTM) );
  dff1BWP I22 (   .Q (P_Q[2]),   .QN (P_QB[2]),   .CDN (INT_RST),   .CP (Q[3]),   .D (OUTP) );
  dffq1BWP I23 (   .Q (Q[4]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[5]) );
  dff1BWP I24 (   .Q (N_Q[3]),   .QN (N_QB[3]),   .CDN (INT_RST),   .CP (Q[4]),   .D (OUTM) );
  dff1BWP I25 (   .Q (P_Q[3]),   .QN (P_QB[3]),   .CDN (INT_RST),   .CP (Q[4]),   .D (OUTP) );
  dffq1BWP I26 (   .Q (Q[5]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[6]) );
  dff1BWP I27 (   .Q (N_Q[4]),   .QN (N_QB[4]),   .CDN (INT_RST),   .CP (Q[5]),   .D (OUTM) );
  dff1BWP I28 (   .Q (P_Q[4]),   .QN (P_QB[4]),   .CDN (INT_RST),   .CP (Q[5]),   .D (OUTP) );
  dffq1BWP I29 (   .Q (Q[6]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[7]) );
  dff1BWP I30 (   .Q (N_Q[5]),   .QN (N_QB[5]),   .CDN (INT_RST),   .CP (Q[6]),   .D (OUTM) );
  dff1BWP I31 (   .Q (P_Q[5]),   .QN (P_QB[5]),   .CDN (INT_RST),   .CP (Q[6]),   .D (OUTP) );
  dffq1BWP I32 (   .Q (Q[7]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[8]) );
  dff1BWP I33 (   .Q (N_Q[6]),   .QN (N_QB[6]),   .CDN (INT_RST),   .CP (Q[7]),   .D (OUTM) );
  dff1BWP I34 (   .Q (P_Q[6]),   .QN (P_QB[6]),   .CDN (INT_RST),   .CP (Q[7]),   .D (OUTP) );
  dffq1BWP I35 (   .Q (Q[8]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[9]) );
  dff1BWP I36 (   .Q (N_Q[7]),   .QN (N_QB[7]),   .CDN (INT_RST),   .CP (Q[8]),   .D (OUTM) );
  dff1BWP I37 (   .Q (P_Q[7]),   .QN (P_QB[7]),   .CDN (INT_RST),   .CP (Q[8]),   .D (OUTP) );
  dffq1BWP I38 (   .Q (Q[9]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[10]) );
  dff1BWP I39 (   .Q (N_Q[8]),   .QN (N_QB[8]),   .CDN (INT_RST),   .CP (Q[9]),   .D (OUTM) );
  dff1BWP I40 (   .Q (P_Q[8]),   .QN (P_QB[8]),   .CDN (INT_RST),   .CP (Q[9]),   .D (OUTP) );
  dffq1BWP I41 (   .Q (Q[10]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[11]) );
  dff1BWP I42 (   .Q (N_Q[9]),   .QN (N_QB[9]),   .CDN (INT_RST),   .CP (Q[10]),   .D (OUTM) );
  dff1BWP I43 (   .Q (P_Q[9]),   .QN (P_QB[9]),   .CDN (INT_RST),   .CP (Q[10]),   .D (OUTP) );
  dffq1BWP I44 (   .Q (Q[11]),   .CDN (INT_RST),   .CP (RDY),   .D (Q[12]) );
  dff1BWP I45 (   .Q (N_Q[10]),   .QN (N_QB[10]),   .CDN (INT_RST),   .CP (Q[11]),   .D (OUTM) );
  dff1BWP I46 (   .Q (P_Q[10]),   .QN (P_QB[10]),   .CDN (INT_RST),   .CP (Q[11]),   .D (OUTP) );
  in1BWP I47 (   .I (N[0]),   .ZN (result[0]) );
  in1BWP I48 (   .I (N_Q[1]),   .ZN (result[1]) );
  in1BWP I49 (   .I (N_Q[2]),   .ZN (result[2]) );
  in1BWP I50 (   .I (N_Q[3]),   .ZN (result[3]) );
  in1BWP I51 (   .I (N_Q[4]),   .ZN (result[4]) );
  in1BWP I52 (   .I (N_Q[5]),   .ZN (result[5]) );
  in1BWP I53 (   .I (N_Q[6]),   .ZN (result[6]) );
  in1BWP I54 (   .I (N_Q[7]),   .ZN (result[7]) );
  in1BWP I55 (   .I (N_Q[8]),   .ZN (result[8]) );
  in1BWP I56 (   .I (N_Q[9]),   .ZN (result[9]) );
  in1BWP I57 (   .I (N_Q[10]),   .ZN (result[10]) );
  nand23BWP I58 (   .ZN (clkc),   .A1 (Q[12]),   .A2 (clock) );
  in6BWP I59 (   .ZN (clk_sample),   .I (clk_sample_b) );
  in2BWP I60 (   .ZN (switch_refn_l[0]),   .I (refn[0]) );
  in2BWP I61 (   .ZN (switch_refn_r[0]),   .I (refn[0]) );
  in2BWP I62 (   .ZN (switch_refp_l[0]),   .I (refp[0]) );
  in2BWP I63 (   .ZN (switch_refp_r[0]),   .I (refp[0]) );
  in2BWP I64 (   .ZN (switch_p[0]),   .I (N_QB[1]) );
  in2BWP I65 (   .ZN (switch_n[0]),   .I (P_QB[1]) );
  in2BWP I66 (   .ZN (switch_bp[0]),   .I (N_Q[1]) );
  in2BWP I67 (   .ZN (switch_bn[0]),   .I (P_Q[1]) );
  nand21BWP I68 (   .ZN (refn_b[0]),   .A1 (P_QB[1]),   .A2 (N_QB[1]) );
  nor21BWP I69 (   .ZN (refp_b[0]),   .A1 (P_Q[1]),   .A2 (N_Q[1]) );
  in1BWP I70 (   .ZN (refn[0]),   .I (refn_b[0]) );
  in1BWP I71 (   .ZN (refp[0]),   .I (refp_b[0]) );
  in2BWP I72 (   .ZN (switch_refn_l[1]),   .I (refn[1]) );
  in2BWP I73 (   .ZN (switch_refn_r[1]),   .I (refn[1]) );
  in2BWP I74 (   .ZN (switch_refp_l[1]),   .I (refp[1]) );
  in2BWP I75 (   .ZN (switch_refp_r[1]),   .I (refp[1]) );
  in2BWP I76 (   .ZN (switch_p[1]),   .I (N_QB[2]) );
  in2BWP I77 (   .ZN (switch_n[1]),   .I (P_QB[2]) );
  in2BWP I78 (   .ZN (switch_bp[1]),   .I (N_Q[2]) );
  in2BWP I79 (   .ZN (switch_bn[1]),   .I (P_Q[2]) );
  nand21BWP I80 (   .ZN (refn_b[1]),   .A1 (P_QB[2]),   .A2 (N_QB[2]) );
  nor21BWP I81 (   .ZN (refp_b[1]),   .A1 (P_Q[2]),   .A2 (N_Q[2]) );
  in1BWP I82 (   .ZN (refn[1]),   .I (refn_b[1]) );
  in1BWP I83 (   .ZN (refp[1]),   .I (refp_b[1]) );
  in2BWP I84 (   .ZN (switch_refn_l[2]),   .I (refn[2]) );
  in2BWP I85 (   .ZN (switch_refn_r[2]),   .I (refn[2]) );
  in2BWP I86 (   .ZN (switch_refp_l[2]),   .I (refp[2]) );
  in2BWP I87 (   .ZN (switch_refp_r[2]),   .I (refp[2]) );
  in2BWP I88 (   .ZN (switch_p[2]),   .I (N_QB[3]) );
  in2BWP I89 (   .ZN (switch_n[2]),   .I (P_QB[3]) );
  in2BWP I90 (   .ZN (switch_bp[2]),   .I (N_Q[3]) );
  in2BWP I91 (   .ZN (switch_bn[2]),   .I (P_Q[3]) );
  nand21BWP I92 (   .ZN (refn_b[2]),   .A1 (P_QB[3]),   .A2 (N_QB[3]) );
  nor21BWP I93 (   .ZN (refp_b[2]),   .A1 (P_Q[3]),   .A2 (N_Q[3]) );
  in1BWP I94 (   .ZN (refn[2]),   .I (refn_b[2]) );
  in1BWP I95 (   .ZN (refp[2]),   .I (refp_b[2]) );
  in2BWP I96 (   .ZN (switch_refn_l[3]),   .I (refn[3]) );
  in2BWP I97 (   .ZN (switch_refn_r[3]),   .I (refn[3]) );
  in2BWP I98 (   .ZN (switch_refp_l[3]),   .I (refp[3]) );
  in2BWP I99 (   .ZN (switch_refp_r[3]),   .I (refp[3]) );
  in2BWP I100 (   .ZN (switch_p[3]),   .I (N_QB[4]) );
  in2BWP I101 (   .ZN (switch_n[3]),   .I (P_QB[4]) );
  in2BWP I102 (   .ZN (switch_bp[3]),   .I (N_Q[4]) );
  in2BWP I103 (   .ZN (switch_bn[3]),   .I (P_Q[4]) );
  nand21BWP I104 (   .ZN (refn_b[3]),   .A1 (P_QB[4]),   .A2 (N_QB[4]) );
  nor21BWP I105 (   .ZN (refp_b[3]),   .A1 (P_Q[4]),   .A2 (N_Q[4]) );
  in1BWP I106 (   .ZN (refn[3]),   .I (refn_b[3]) );
  in1BWP I107 (   .ZN (refp[3]),   .I (refp_b[3]) );
  in2BWP I108 (   .ZN (switch_refn_l[4]),   .I (refn[4]) );
  in2BWP I109 (   .ZN (switch_refn_r[4]),   .I (refn[4]) );
  in2BWP I110 (   .ZN (switch_refp_l[4]),   .I (refp[4]) );
  in2BWP I111 (   .ZN (switch_refp_r[4]),   .I (refp[4]) );
  in2BWP I112 (   .ZN (switch_p[4]),   .I (N_QB[5]) );
  in2BWP I113 (   .ZN (switch_n[4]),   .I (P_QB[5]) );
  in2BWP I114 (   .ZN (switch_bp[4]),   .I (N_Q[5]) );
  in2BWP I115 (   .ZN (switch_bn[4]),   .I (P_Q[5]) );
  nand21BWP I116 (   .ZN (refn_b[4]),   .A1 (P_QB[5]),   .A2 (N_QB[5]) );
  nor21BWP I117 (   .ZN (refp_b[4]),   .A1 (P_Q[5]),   .A2 (N_Q[5]) );
  in1BWP I118 (   .ZN (refn[4]),   .I (refn_b[4]) );
  in1BWP I119 (   .ZN (refp[4]),   .I (refp_b[4]) );
  in2BWP I120 (   .ZN (switch_refn_l[5]),   .I (refn[5]) );
  in2BWP I121 (   .ZN (switch_refn_r[5]),   .I (refn[5]) );
  in2BWP I122 (   .ZN (switch_refp_l[5]),   .I (refp[5]) );
  in2BWP I123 (   .ZN (switch_refp_r[5]),   .I (refp[5]) );
  in2BWP I124 (   .ZN (switch_p[5]),   .I (N_QB[6]) );
  in2BWP I125 (   .ZN (switch_n[5]),   .I (P_QB[6]) );
  in2BWP I126 (   .ZN (switch_bp[5]),   .I (N_Q[6]) );
  in2BWP I127 (   .ZN (switch_bn[5]),   .I (P_Q[6]) );
  nand21BWP I128 (   .ZN (refn_b[5]),   .A1 (P_QB[6]),   .A2 (N_QB[6]) );
  nor21BWP I129 (   .ZN (refp_b[5]),   .A1 (P_Q[6]),   .A2 (N_Q[6]) );
  in1BWP I130 (   .ZN (refn[5]),   .I (refn_b[5]) );
  in1BWP I131 (   .ZN (refp[5]),   .I (refp_b[5]) );
  in2BWP I132 (   .ZN (switch_refn_l[6]),   .I (refn[6]) );
  in2BWP I133 (   .ZN (switch_refn_r[6]),   .I (refn[6]) );
  in2BWP I134 (   .ZN (switch_refp_l[6]),   .I (refp[6]) );
  in2BWP I135 (   .ZN (switch_refp_r[6]),   .I (refp[6]) );
  in2BWP I136 (   .ZN (switch_p[6]),   .I (N_QB[7]) );
  in2BWP I137 (   .ZN (switch_n[6]),   .I (P_QB[7]) );
  in2BWP I138 (   .ZN (switch_bp[6]),   .I (N_Q[7]) );
  in2BWP I139 (   .ZN (switch_bn[6]),   .I (P_Q[7]) );
  nand21BWP I140 (   .ZN (refn_b[6]),   .A1 (P_QB[7]),   .A2 (N_QB[7]) );
  nor21BWP I141 (   .ZN (refp_b[6]),   .A1 (P_Q[7]),   .A2 (N_Q[7]) );
  in1BWP I142 (   .ZN (refn[6]),   .I (refn_b[6]) );
  in1BWP I143 (   .ZN (refp[6]),   .I (refp_b[6]) );
  in2BWP I144 (   .ZN (switch_refn_l[7]),   .I (refn[7]) );
  in2BWP I145 (   .ZN (switch_refn_r[7]),   .I (refn[7]) );
  in2BWP I146 (   .ZN (switch_refp_l[7]),   .I (refp[7]) );
  in2BWP I147 (   .ZN (switch_refp_r[7]),   .I (refp[7]) );
  in2BWP I148 (   .ZN (switch_p[7]),   .I (N_QB[8]) );
  in2BWP I149 (   .ZN (switch_n[7]),   .I (P_QB[8]) );
  in2BWP I150 (   .ZN (switch_bp[7]),   .I (N_Q[8]) );
  in2BWP I151 (   .ZN (switch_bn[7]),   .I (P_Q[8]) );
  nand21BWP I152 (   .ZN (refn_b[7]),   .A1 (P_QB[8]),   .A2 (N_QB[8]) );
  nor21BWP I153 (   .ZN (refp_b[7]),   .A1 (P_Q[8]),   .A2 (N_Q[8]) );
  in1BWP I154 (   .ZN (refn[7]),   .I (refn_b[7]) );
  in1BWP I155 (   .ZN (refp[7]),   .I (refp_b[7]) );
  in3BWP I156 (   .ZN (switch_refn_l[8]),   .I (refn[8]) );
  in3BWP I157 (   .ZN (switch_refn_r[8]),   .I (refn[8]) );
  in3BWP I158 (   .ZN (switch_refp_l[8]),   .I (refp[8]) );
  in3BWP I159 (   .ZN (switch_refp_r[8]),   .I (refp[8]) );
  in3BWP I160 (   .ZN (switch_p[8]),   .I (N_B[9]) );
  in3BWP I161 (   .ZN (switch_n[8]),   .I (P_B[9]) );
  in3BWP I162 (   .ZN (switch_bp[8]),   .I (N[9]) );
  in3BWP I163 (   .ZN (switch_bn[8]),   .I (P[9]) );
  nand21BWP I164 (   .ZN (refn_b[8]),   .A1 (P_B[9]),   .A2 (N_B[9]) );
  nor21BWP I165 (   .ZN (refp_b[8]),   .A1 (P[9]),   .A2 (N[9]) );
  in2BWP I166 (   .ZN (refn[8]),   .I (refn_b[8]) );
  in2BWP I167 (   .ZN (refp[8]),   .I (refp_b[8]) );
  in1BWP I168 (   .ZN (P_B[9]),   .I (P_Q[9]) );
  in1BWP I169 (   .ZN (P[9]),   .I (P_QB[9]) );
  in1BWP I170 (   .ZN (N_B[9]),   .I (N_Q[9]) );
  in1BWP I171 (   .ZN (N[9]),   .I (N_QB[9]) );
  in4BWP I172 (   .ZN (switch_refn_l[9]),   .I (refn[9]) );
  in4BWP I173 (   .ZN (switch_refn_r[9]),   .I (refn[9]) );
  in4BWP I174 (   .ZN (switch_refp_l[9]),   .I (refp[9]) );
  in4BWP I175 (   .ZN (switch_refp_r[9]),   .I (refp[9]) );
  in4BWP I176 (   .ZN (switch_p[9]),   .I (N_B[10]) );
  in4BWP I177 (   .ZN (switch_n[9]),   .I (P_B[10]) );
  in4BWP I178 (   .ZN (switch_bp[9]),   .I (N[10]) );
  in4BWP I179 (   .ZN (switch_bn[9]),   .I (P[10]) );
  nand21BWP I180 (   .ZN (refn_b[9]),   .A1 (P_B[10]),   .A2 (N_B[10]) );
  nor21BWP I181 (   .ZN (refp_b[9]),   .A1 (P[10]),   .A2 (N[10]) );
  in2BWP I182 (   .ZN (refn[9]),   .I (refn_b[9]) );
  in2BWP I183 (   .ZN (refp[9]),   .I (refp_b[9]) );
  in1BWP I184 (   .ZN (P_B[10]),   .I (P_Q[10]) );
  in1BWP I185 (   .ZN (P[10]),   .I (P_QB[10]) );
  in1BWP I186 (   .ZN (N_B[10]),   .I (N_Q[10]) );
  in1BWP I187 (   .ZN (N[10]),   .I (N_QB[10]) );

endmodule

