
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
  DFCND1BWP I0 (   .Q (Q[1]),   .QN (QB),   .CDN (INT_RST),   .CP (clock),   .D (Q[2]) );
  DFCNQD4BWP I1 (   .Q (N[0]),   .CDN (INT_RST),   .CP (Q[1]),   .D (OUTM) );
  DFCNQD4BWP I2 (   .Q (P[0]),   .CDN (INT_RST),   .CP (Q[1]),   .D (OUTP) );
  INVD4BWP I3 (   .ZN (clock_output),   .I (net07) );
  DEL025D1BWP I4 (   .Z (net07),   .I (net039) );
  DFCNQD1BWP I5 (   .Q (INT_RST),   .CDN (reset_n),   .CP (SYS_CLKB),   .D (QB) );
  DFCND1BWP I6 (   .Q (Q[12]),   .QN (QB_12),   .CDN (INT_RST),   .CP (clock),   .D (high_net) );
  INVD2BWP I7 (   .ZN (clk_sample_b),   .I (QB_12) );
  TIEHBWP I8 (   .Z (high_net) );
  INVD3BWP I9 (   .ZN (SYS_CLKB),   .I (clock) );
  ND2D0BWP I10 (   .ZN (OUTP),   .A1 (cmp_p),   .A2 (OUTM) );
  ND2D0BWP I11 (   .ZN (OUTM),   .A1 (OUTP),   .A2 (cmp_n) );
  NR2D0BWP I12 (   .ZN (net039),   .A1 (P[0]),   .A2 (N[0]) );
  AN2D2BWP I13 (   .Z (refn[0]),   .A1 (P_B[1]),   .A2 (N_B[1]) );
  OR2D2BWP I14 (   .Z (refp[0]),   .A1 (P[1]),   .A2 (N[1]) );
  DFCNQD1BWP I15 (   .Q (Q[2]),   .CDN (INT_RST),   .CP (clock),   .D (Q[3]) );
  DFCND4BWP I16 (   .Q (N[1]),   .QN (N_B[1]),   .CDN (INT_RST),   .CP (Q[2]),   .D (OUTM) );
  DFCND4BWP I17 (   .Q (P[1]),   .QN (P_B[1]),   .CDN (INT_RST),   .CP (Q[2]),   .D (OUTP) );
  AN2D2BWP I18 (   .Z (refn[1]),   .A1 (P_B[2]),   .A2 (N_B[2]) );
  OR2D2BWP I19 (   .Z (refp[1]),   .A1 (P[2]),   .A2 (N[2]) );
  DFCNQD1BWP I20 (   .Q (Q[3]),   .CDN (INT_RST),   .CP (clock),   .D (Q[4]) );
  DFCND4BWP I21 (   .Q (N[2]),   .QN (N_B[2]),   .CDN (INT_RST),   .CP (Q[3]),   .D (OUTM) );
  DFCND4BWP I22 (   .Q (P[2]),   .QN (P_B[2]),   .CDN (INT_RST),   .CP (Q[3]),   .D (OUTP) );
  AN2D2BWP I23 (   .Z (refn[2]),   .A1 (P_B[3]),   .A2 (N_B[3]) );
  OR2D2BWP I24 (   .Z (refp[2]),   .A1 (P[3]),   .A2 (N[3]) );
  DFCNQD1BWP I25 (   .Q (Q[4]),   .CDN (INT_RST),   .CP (clock),   .D (Q[5]) );
  DFCND4BWP I26 (   .Q (N[3]),   .QN (N_B[3]),   .CDN (INT_RST),   .CP (Q[4]),   .D (OUTM) );
  DFCND4BWP I27 (   .Q (P[3]),   .QN (P_B[3]),   .CDN (INT_RST),   .CP (Q[4]),   .D (OUTP) );
  AN2D2BWP I28 (   .Z (refn[3]),   .A1 (P_B[4]),   .A2 (N_B[4]) );
  OR2D2BWP I29 (   .Z (refp[3]),   .A1 (P[4]),   .A2 (N[4]) );
  DFCNQD1BWP I30 (   .Q (Q[5]),   .CDN (INT_RST),   .CP (clock),   .D (Q[6]) );
  DFCND4BWP I31 (   .Q (N[4]),   .QN (N_B[4]),   .CDN (INT_RST),   .CP (Q[5]),   .D (OUTM) );
  DFCND4BWP I32 (   .Q (P[4]),   .QN (P_B[4]),   .CDN (INT_RST),   .CP (Q[5]),   .D (OUTP) );
  AN2D2BWP I33 (   .Z (refn[4]),   .A1 (P_B[5]),   .A2 (N_B[5]) );
  OR2D2BWP I34 (   .Z (refp[4]),   .A1 (P[5]),   .A2 (N[5]) );
  DFCNQD1BWP I35 (   .Q (Q[6]),   .CDN (INT_RST),   .CP (clock),   .D (Q[7]) );
  DFCND4BWP I36 (   .Q (N[5]),   .QN (N_B[5]),   .CDN (INT_RST),   .CP (Q[6]),   .D (OUTM) );
  DFCND4BWP I37 (   .Q (P[5]),   .QN (P_B[5]),   .CDN (INT_RST),   .CP (Q[6]),   .D (OUTP) );
  AN2D2BWP I38 (   .Z (refn[5]),   .A1 (P_B[6]),   .A2 (N_B[6]) );
  OR2D2BWP I39 (   .Z (refp[5]),   .A1 (P[6]),   .A2 (N[6]) );
  DFCNQD1BWP I40 (   .Q (Q[7]),   .CDN (INT_RST),   .CP (clock),   .D (Q[8]) );
  DFCND4BWP I41 (   .Q (N[6]),   .QN (N_B[6]),   .CDN (INT_RST),   .CP (Q[7]),   .D (OUTM) );
  DFCND4BWP I42 (   .Q (P[6]),   .QN (P_B[6]),   .CDN (INT_RST),   .CP (Q[7]),   .D (OUTP) );
  AN2D2BWP I43 (   .Z (refn[6]),   .A1 (P_B[7]),   .A2 (N_B[7]) );
  OR2D2BWP I44 (   .Z (refp[6]),   .A1 (P[7]),   .A2 (N[7]) );
  DFCNQD1BWP I45 (   .Q (Q[8]),   .CDN (INT_RST),   .CP (clock),   .D (Q[9]) );
  DFCND4BWP I46 (   .Q (N[7]),   .QN (N_B[7]),   .CDN (INT_RST),   .CP (Q[8]),   .D (OUTM) );
  DFCND4BWP I47 (   .Q (P[7]),   .QN (P_B[7]),   .CDN (INT_RST),   .CP (Q[8]),   .D (OUTP) );
  AN2D2BWP I48 (   .Z (refn[7]),   .A1 (P_B[8]),   .A2 (N_B[8]) );
  OR2D2BWP I49 (   .Z (refp[7]),   .A1 (P[8]),   .A2 (N[8]) );
  DFCNQD1BWP I50 (   .Q (Q[9]),   .CDN (INT_RST),   .CP (clock),   .D (Q[10]) );
  DFCND4BWP I51 (   .Q (N[8]),   .QN (N_B[8]),   .CDN (INT_RST),   .CP (Q[9]),   .D (OUTM) );
  DFCND4BWP I52 (   .Q (P[8]),   .QN (P_B[8]),   .CDN (INT_RST),   .CP (Q[9]),   .D (OUTP) );
  AN2D2BWP I53 (   .Z (refn[8]),   .A1 (P_B[9]),   .A2 (N_B[9]) );
  OR2D2BWP I54 (   .Z (refp[8]),   .A1 (P[9]),   .A2 (N[9]) );
  DFCNQD1BWP I55 (   .Q (Q[10]),   .CDN (INT_RST),   .CP (clock),   .D (Q[11]) );
  DFCND4BWP I56 (   .Q (N[9]),   .QN (N_B[9]),   .CDN (INT_RST),   .CP (Q[10]),   .D (OUTM) );
  DFCND4BWP I57 (   .Q (P[9]),   .QN (P_B[9]),   .CDN (INT_RST),   .CP (Q[10]),   .D (OUTP) );
  AN2D2BWP I58 (   .Z (refn[9]),   .A1 (P_B[10]),   .A2 (N_B[10]) );
  OR2D2BWP I59 (   .Z (refp[9]),   .A1 (P[10]),   .A2 (N[10]) );
  DFCNQD1BWP I60 (   .Q (Q[11]),   .CDN (INT_RST),   .CP (clock),   .D (Q[12]) );
  DFCND4BWP I61 (   .Q (N[10]),   .QN (N_B[10]),   .CDN (INT_RST),   .CP (Q[11]),   .D (OUTM) );
  DFCND4BWP I62 (   .Q (P[10]),   .QN (P_B[10]),   .CDN (INT_RST),   .CP (Q[11]),   .D (OUTP) );
  INVD1BWP I63 (   .I (N[0]),   .ZN (result[0]) );
  INVD1BWP I64 (   .I (N[1]),   .ZN (result[1]) );
  INVD1BWP I65 (   .I (N[2]),   .ZN (result[2]) );
  INVD1BWP I66 (   .I (N[3]),   .ZN (result[3]) );
  INVD1BWP I67 (   .I (N[4]),   .ZN (result[4]) );
  INVD1BWP I68 (   .I (N[5]),   .ZN (result[5]) );
  INVD1BWP I69 (   .I (N[6]),   .ZN (result[6]) );
  INVD1BWP I70 (   .I (N[7]),   .ZN (result[7]) );
  INVD1BWP I71 (   .I (N[8]),   .ZN (result[8]) );
  INVD1BWP I72 (   .I (N[9]),   .ZN (result[9]) );
  INVD1BWP I73 (   .I (N[10]),   .ZN (result[10]) );
  ND2D3BWP I74 (   .ZN (clkc),   .A1 (Q[12]),   .A2 (clock) );
  INVD6BWP I75 (   .ZN (clk_sample),   .I (clk_sample_b) );
  INVD2BWP I76 (   .ZN (switch_refn_l[0]),   .I (refn[0]) );
  INVD2BWP I77 (   .ZN (switch_refn_r[0]),   .I (refn[0]) );
  INVD2BWP I78 (   .ZN (switch_refp_l[0]),   .I (refp[0]) );
  INVD2BWP I79 (   .ZN (switch_refp_r[0]),   .I (refp[0]) );
  INVD2BWP I80 (   .ZN (switch_p[0]),   .I (N_B[1]) );
  INVD2BWP I81 (   .ZN (switch_n[0]),   .I (P_B[1]) );
  INVD2BWP I82 (   .ZN (switch_bp[0]),   .I (N[1]) );
  INVD2BWP I83 (   .ZN (switch_bn[0]),   .I (P[1]) );
  INVD2BWP I84 (   .ZN (switch_refn_l[1]),   .I (refn[1]) );
  INVD2BWP I85 (   .ZN (switch_refn_r[1]),   .I (refn[1]) );
  INVD2BWP I86 (   .ZN (switch_refp_l[1]),   .I (refp[1]) );
  INVD2BWP I87 (   .ZN (switch_refp_r[1]),   .I (refp[1]) );
  INVD2BWP I88 (   .ZN (switch_p[1]),   .I (N_B[2]) );
  INVD2BWP I89 (   .ZN (switch_n[1]),   .I (P_B[2]) );
  INVD2BWP I90 (   .ZN (switch_bp[1]),   .I (N[2]) );
  INVD2BWP I91 (   .ZN (switch_bn[1]),   .I (P[2]) );
  INVD2BWP I92 (   .ZN (switch_refn_l[2]),   .I (refn[2]) );
  INVD2BWP I93 (   .ZN (switch_refn_r[2]),   .I (refn[2]) );
  INVD2BWP I94 (   .ZN (switch_refp_l[2]),   .I (refp[2]) );
  INVD2BWP I95 (   .ZN (switch_refp_r[2]),   .I (refp[2]) );
  INVD2BWP I96 (   .ZN (switch_p[2]),   .I (N_B[3]) );
  INVD2BWP I97 (   .ZN (switch_n[2]),   .I (P_B[3]) );
  INVD2BWP I98 (   .ZN (switch_bp[2]),   .I (N[3]) );
  INVD2BWP I99 (   .ZN (switch_bn[2]),   .I (P[3]) );
  INVD2BWP I100 (   .ZN (switch_refn_l[3]),   .I (refn[3]) );
  INVD2BWP I101 (   .ZN (switch_refn_r[3]),   .I (refn[3]) );
  INVD2BWP I102 (   .ZN (switch_refp_l[3]),   .I (refp[3]) );
  INVD2BWP I103 (   .ZN (switch_refp_r[3]),   .I (refp[3]) );
  INVD2BWP I104 (   .ZN (switch_p[3]),   .I (N_B[4]) );
  INVD2BWP I105 (   .ZN (switch_n[3]),   .I (P_B[4]) );
  INVD2BWP I106 (   .ZN (switch_bp[3]),   .I (N[4]) );
  INVD2BWP I107 (   .ZN (switch_bn[3]),   .I (P[4]) );
  INVD2BWP I108 (   .ZN (switch_refn_l[4]),   .I (refn[4]) );
  INVD2BWP I109 (   .ZN (switch_refn_r[4]),   .I (refn[4]) );
  INVD2BWP I110 (   .ZN (switch_refp_l[4]),   .I (refp[4]) );
  INVD2BWP I111 (   .ZN (switch_refp_r[4]),   .I (refp[4]) );
  INVD2BWP I112 (   .ZN (switch_p[4]),   .I (N_B[5]) );
  INVD2BWP I113 (   .ZN (switch_n[4]),   .I (P_B[5]) );
  INVD2BWP I114 (   .ZN (switch_bp[4]),   .I (N[5]) );
  INVD2BWP I115 (   .ZN (switch_bn[4]),   .I (P[5]) );
  INVD2BWP I116 (   .ZN (switch_refn_l[5]),   .I (refn[5]) );
  INVD2BWP I117 (   .ZN (switch_refn_r[5]),   .I (refn[5]) );
  INVD2BWP I118 (   .ZN (switch_refp_l[5]),   .I (refp[5]) );
  INVD2BWP I119 (   .ZN (switch_refp_r[5]),   .I (refp[5]) );
  INVD2BWP I120 (   .ZN (switch_p[5]),   .I (N_B[6]) );
  INVD2BWP I121 (   .ZN (switch_n[5]),   .I (P_B[6]) );
  INVD2BWP I122 (   .ZN (switch_bp[5]),   .I (N[6]) );
  INVD2BWP I123 (   .ZN (switch_bn[5]),   .I (P[6]) );
  INVD2BWP I124 (   .ZN (switch_refn_l[6]),   .I (refn[6]) );
  INVD2BWP I125 (   .ZN (switch_refn_r[6]),   .I (refn[6]) );
  INVD2BWP I126 (   .ZN (switch_refp_l[6]),   .I (refp[6]) );
  INVD2BWP I127 (   .ZN (switch_refp_r[6]),   .I (refp[6]) );
  INVD2BWP I128 (   .ZN (switch_p[6]),   .I (N_B[7]) );
  INVD2BWP I129 (   .ZN (switch_n[6]),   .I (P_B[7]) );
  INVD2BWP I130 (   .ZN (switch_bp[6]),   .I (N[7]) );
  INVD2BWP I131 (   .ZN (switch_bn[6]),   .I (P[7]) );
  INVD2BWP I132 (   .ZN (switch_refn_l[7]),   .I (refn[7]) );
  INVD2BWP I133 (   .ZN (switch_refn_r[7]),   .I (refn[7]) );
  INVD2BWP I134 (   .ZN (switch_refp_l[7]),   .I (refp[7]) );
  INVD2BWP I135 (   .ZN (switch_refp_r[7]),   .I (refp[7]) );
  INVD2BWP I136 (   .ZN (switch_p[7]),   .I (N_B[8]) );
  INVD2BWP I137 (   .ZN (switch_n[7]),   .I (P_B[8]) );
  INVD2BWP I138 (   .ZN (switch_bp[7]),   .I (N[8]) );
  INVD2BWP I139 (   .ZN (switch_bn[7]),   .I (P[8]) );
  INVD3BWP I140 (   .ZN (switch_refn_l[8]),   .I (refn[8]) );
  INVD3BWP I141 (   .ZN (switch_refn_r[8]),   .I (refn[8]) );
  INVD3BWP I142 (   .ZN (switch_refp_l[8]),   .I (refp[8]) );
  INVD3BWP I143 (   .ZN (switch_refp_r[8]),   .I (refp[8]) );
  INVD3BWP I144 (   .ZN (switch_p[8]),   .I (N_B[9]) );
  INVD3BWP I145 (   .ZN (switch_n[8]),   .I (P_B[9]) );
  INVD3BWP I146 (   .ZN (switch_bp[8]),   .I (N[9]) );
  INVD3BWP I147 (   .ZN (switch_bn[8]),   .I (P[9]) );
  INVD4BWP I148 (   .ZN (switch_refn_l[9]),   .I (refn[9]) );
  INVD4BWP I149 (   .ZN (switch_refn_r[9]),   .I (refn[9]) );
  INVD4BWP I150 (   .ZN (switch_refp_l[9]),   .I (refp[9]) );
  INVD4BWP I151 (   .ZN (switch_refp_r[9]),   .I (refp[9]) );
  INVD4BWP I152 (   .ZN (switch_p[9]),   .I (N_B[10]) );
  INVD4BWP I153 (   .ZN (switch_n[9]),   .I (P_B[10]) );
  INVD4BWP I154 (   .ZN (switch_bp[9]),   .I (N[10]) );
  INVD4BWP I155 (   .ZN (switch_bn[9]),   .I (P[10]) );

endmodule

