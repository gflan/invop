\ENCODING=ISO-8859-1
\Problem name:

Maximize
obj:   700 x_pp_ln + 700 x_pp_mn + 700 x_pp_hn + 700 x_pp_rg + 700 x_pp_cg
        + 600 x_rp_ln + 600 x_rp_mn + 600 x_rp_hn + 600 x_rp_rg + 600 x_rp_cg
        + 400 x_jf_lo + 400 x_jf_ho + 400 x_jf_co + 400 x_jf_res
        + 350 x_fo + 150 x_lube

Subject To
c1:     x_dest_1 + x_dest_2 <= 45000
c2:     x_ref_ln + x_ref_mn + x_ref_hn <= 10000
c3:     x_cr_lo + x_cr_ho <= 8000
c4:     x_pp_ln + x_pp_mn + x_pp_hn + x_pp_rg + x_pp_cg - 0.4 x_rp_ln - 0.4 x_rp_mn - 0.4 x_rp_hn - 0.4 x_rp_rg - 0.4 x_rp_cg >= 0
c5:     x_ref_ln + x_pp_ln + x_rp_ln - 0.1 x_dest_1 - 0.15 x_dest_2 <= 0
c6:     x_ref_mn + x_pp_mn + x_rp_mn - 0.2 x_dest_1 - 0.25 x_dest_2 <= 0
c7:     x_ref_hn + x_pp_hn + x_rp_hn - 0.2 x_dest_1 - 0.18 x_dest_2 <= 0
c8:     x_jf_lo + 0.5555555555555556 x_fo + x_cr_lo - 0.12 x_dest_1 - 0.08 x_dest_2 <= 0
c9:     x_jf_ho + 0.16666666666666666 x_fo + x_cr_ho - 0.2 x_dest_1 - 0.19 x_dest_2 <= 0
c10:    x_jf_res + x_lube + 0.05555555555555555 x_fo - 0.13 x_dest_1 - 0.12 x_dest_2 <= 0
c11:    x_pp_rg + x_rp_rg - 0.6 x_ref_ln - 0.52 x_ref_mn - 0.45 x_ref_hn <= 0
c12:    x_pp_cg + x_rp_cg - 0.68 x_cr_lo - 0.28 x_cr_ho <= 0
c13:    x_jf_co + 0.2222222222222222 x_fo - 0.75 x_cr_lo - 0.2 x_cr_ho <= 0
c14:    6 x_rp_ln - 4 x_rp_mn - 14 x_rp_hn + 31 x_rp_rg + 21 x_rp_cg >= 0
c15:    -4 x_pp_ln - 14 x_pp_mn - 24 x_pp_hn + 21 x_pp_rg + 11 x_pp_cg >= 0
c16:    -0.4 x_jf_ho + 0.5 x_jf_co - 0.95 x_jf_res <= 0

Bounds
0 <= x_dest_1 <= 20000
0 <= x_dest_2 <= 30000
500 <= x_lube <= 1000

End
