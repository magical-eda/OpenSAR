`timescale 1ns/10ps

module sar_logic(clock, reset_n, cmp_decision, clk_sample, result, switch_p, switch_n, switch_bp, switch_bn, switch_refp, switch_refn);

    parameter BITS = 9;
    parameter ZERO = 9'b0;
    parameter ZERO_RES = 10'b0;
    parameter ONE = 9'b1_0000_0000;
    parameter reset_state = 0, sample_state = 1, convert_state = 2;

    input clock;
    input reset_n;
    input cmp_decision;

    output clk_sample;
    output [BITS:0] result;
    output [BITS-1:0] switch_p;
    output [BITS-1:0] switch_n;
    output [BITS-1:0] switch_bp;
    output [BITS-1:0] switch_bn;
    output [BITS-1:0] switch_refn;
    output [BITS-1:0] switch_refp;

    reg clk_sample;
    reg [BITS:0] result;
    
    reg [BITS-1:0] switch_p;
    reg [BITS-1:0] switch_n;
    reg [BITS-1:0] sar;
    reg [2:0] state;

    always @ (posedge clock) 
    begin
        if(!reset_n)
        begin
            clk_sample <= 1'b0;
            result <= ZERO_RES;
            switch_p <= ZERO;
            switch_n <= ZERO;
            sar <= ZERO;
            state <= 3'b0;
        end
        else
        begin
            case(state)
                reset_state: 
                    state <= sample_state;
                sample_state:
                begin
                    clk_sample <= 1'b1;
                    sar <= ZERO;
                    switch_p <= ZERO;
                    switch_n <= ZERO;
                    state <= convert_state;
                    result [BITS:1] <= switch_p[BITS-1:0];
                    result[0] <= cmp_decision;
                end
                convert_state:
                begin
                    clk_sample <= 1'b0;
                    if (sar == ZERO)
                        sar <= ONE;
                    else
                        sar <= sar >> 1;
                    if (cmp_decision)
                    begin
                        switch_p <= switch_p | sar;
                        switch_n <= switch_n & (~sar);
                    end
                    else
                        switch_n <= switch_n | sar;
                    if (sar[0])
                        state <= sample_state;
                end
                default:
                    state <= sample_state;
            endcase
        end
    end

    assign switch_refp = ~(switch_p | switch_n);
    assign switch_refn = switch_p | switch_n;
    assign switch_bp = ~switch_p;
    assign switch_bn = ~switch_n;

endmodule
    
    
