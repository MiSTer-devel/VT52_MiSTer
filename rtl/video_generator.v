/**
 * 80x24 char generator (8x16 char size) & sync generator


The `video_generator` module is designed to produce a video signal for a VGA display, simulating a 
text-based video output with cursor support and scrolling. Here's a detailed breakdown of its functionality:

### Parameters:
- **`ROWS`**: Number of text rows displayed on the screen (default is 24).
- **`COLS`**: Number of text columns displayed on the screen (default is 80).
- **`ROW_BITS`**: Number of bits to represent row indices (typically calculated as `log2(ROWS)`).
- **`COL_BITS`**: Number of bits to represent column indices (typically calculated as `log2(COLS)`).
- **`ADDR_BITS`**: Number of bits for addressing the character buffer.

### Inputs and Outputs:
- **Inputs**:
  - **`clk`**: Clock signal for the module.
  - **`reset`**: Reset signal to initialize or clear the module state.
  - **`cursor_x`**: Horizontal position of the cursor in text columns.
  - **`cursor_y`**: Vertical position of the cursor in text rows.
  - **`cursor_blink_on`**: Indicates if the cursor should blink.
  - **`first_char`**: Address of the first character in the buffer for scrolling.
  - **`char_buffer_data`**: Data read from the character buffer.
  - **`char_rom_data`**: Data read from the character ROM.

- **Outputs**:
  - **`hsync`**: Horizontal synchronization signal.
  - **`vsync`**: Vertical synchronization signal.
  - **`video`**: Video signal output (pixel data).
  - **`hblank`**: Horizontal blanking signal.
  - **`vblank`**: Vertical blanking signal.
  - **`char_buffer_address`**: Address for reading from the character buffer.
  - **`char_rom_address`**: Address for reading from the character ROM.

### Internal Signals:
- **Timing Constants**: Define VGA signal timings (e.g., horizontal and vertical sync pulses, blanking periods).
- **Counters**: Horizontal and vertical counters (`hc`, `vc`) to keep track of the current pixel location.
- **State Variables**: Track the current row, column, and pixel within characters (`row`, `col`, `rowc`, `colc`).
- **Character Addressing**: Calculate addresses for the character buffer and ROM.

### Key Functionality:

1. **Timing Generation**:
   - **Horizontal and Vertical Counters**: Increment to track the current pixel position. When they reach their maximum values, they reset, and the vertical counter increments or resets as needed.
   - **Sync and Blank Signals**: Based on the counter values, generate the appropriate `hsync`, `vsync`, `hblank`, and `vblank` signals to control the VGA display timing.

2. **Character and Cursor Management**:
   - **Character Addressing**: Calculate addresses for character data based on the current row and column. The `char_buffer_address` and `char_rom_address` are derived from these calculations.
   - **Cursor Handling**: Determine if the current pixel is under the cursor and should be inverted based on the `cursor_blink_on` signal.
   - **Pixel Output**: Combine the character pixel data with the cursor pixel data to produce the final video output. The video signal is only active during non-blanking periods.

3. **Character Generation**:
   - **Pixel Processing**: Read character data from the ROM based on the current character and pixel location within that character.
   - **Row and Column Tracking**: Update the current row, column, and pixel coordinates as pixels are processed.

### Summary:
The `video_generator` module produces VGA-compatible video signals with text display capabilities. 
It manages synchronization, blanking, and pixel data combining text characters and cursor information. 
The module generates horizontal and vertical sync signals, handles cursor positioning and blinking, and 
manages character data retrieval from a buffer and ROM to render text on the screen. This design supports 
text-based displays with basic cursor functionality and scrolling.

 */

module video_generator
  #(parameter ROWS = 24,
    parameter COLS = 80,
    // XXX These could probably be calculated from the above
    parameter ROW_BITS = 5,
    parameter COL_BITS = 7,
    parameter ADDR_BITS = 11
    // first address outside the visible area
    )
   (
    input clk,
    input reset,
    // video output
    output reg hsync,
    output reg vsync,
    output reg video,
    // video output extra info
    output reg hblank,
    output reg vblank,
    // cursor
    input [COL_BITS-1:0] cursor_x,
    input [ROW_BITS-1:0] cursor_y,
    input cursor_blink_on,
    // scrolling
    input [ADDR_BITS-1:0] first_char,
    // char buffer
    output wire [ADDR_BITS-1:0] char_buffer_address,
    input [7:0] char_buffer_data,
    // char rom
    output wire [11:0] char_rom_address,
    input [7:0] char_rom_data
    );
   localparam PAST_LAST_ROW = ROWS * COLS;
   // VGA Signal 640x400 @ 70 Hz timing
   // from http://tinyvga.com/vga-timing/640x400@70Hz
   // Total size, visible size, front and back porches and sync pulse size
   // clk is 24Mhz (half USB...), so about what we need (around 25Mhz)
   localparam hbits = 10;
   localparam hpixels = 800;
   localparam hbp = 48;
   localparam hvisible = 640;
   localparam hfp = 16;
   localparam hpulse = 96;
   // Added 8 to vbp and vfp to compensate for the missing character row
   // (25 * 16 == 400, we are using 24 rows so we are 16 pixels short)
   localparam vbits = 9;
   localparam vlines = 449;
   localparam vbp = 35 + 8;
   localparam vvisible = 400 - 16;
   localparam vfp = 12 + 8;
   localparam vpulse = 2;
   // sync polarity
   localparam hsync_on = 1'b0;
   localparam vsync_on = 1'b1;
   localparam hsync_off = ~hsync_on;
   localparam vsync_off = ~vsync_on;
   // video polarity
   localparam video_on = 1'b1;
   localparam video_off = ~video_on;

   // These are to combine the chars & the cursor for video output
   reg is_under_cursor;
   reg cursor_pixel;
   reg char_pixel;
   reg combined_pixel;

   // horizontal & vertical counters
   reg [hbits-1:0] hc, next_hc;
   reg [vbits-1:0] vc, next_vc;
   // syncs and blanks
   reg next_hblank, next_vblank, next_hsync, next_vsync;
   // character generation
   reg [ROW_BITS-1:0] row, next_row;
   reg [COL_BITS-1:0] col, next_col;
   // these count the rows and cols of pixels inside a char (8x16)
   reg [2:0] colc, next_colc;
   reg [3:0] rowc, next_rowc;
   // maintain the next address to the char buffer
   reg [ADDR_BITS-1:0] char, next_char;

   // we must use next_char instead of char because we need it ready for
   // the next clock cycle
   assign char_buffer_address = next_char;
   // The address of the char row in rom is formed with the char and the row offset
   // we can get away with the addition here because the number of rows
   // in this font is a power of 2 (16 in this case)
   assign char_rom_address = { char_buffer_data, rowc };

   //
   // horizontal & vertical counters, syncs and blanks
   //
   always @(posedge clk) begin
      if (reset) begin
         hc <= 0;
         vc <= 0;
         hsync <= hsync_off;
         vsync <= vsync_off;
         hblank <= 1;
         vblank <= 1;
      end
      else begin
         hc <= next_hc;
         vc <= next_vc;
         hsync <= next_hsync;
         vsync <= next_vsync;
         hblank <= next_hblank;
         vblank <= next_vblank;
      end
   end

   always @(*) begin
      if (hc == hpixels) begin
         next_hc = 0;
         next_vc = (vc == vlines)? 0 : vc + 1;
      end
      else begin
         next_hc = hc + 1;
         next_vc = vc;
      end
      next_hsync = (next_hc >= hbp + hvisible + hfp)? hsync_on : hsync_off;
      next_vsync = (next_vc >= vbp + vvisible + vfp)? vsync_on : vsync_off;
      next_hblank = (next_hc < hbp || next_hc >= hbp + hvisible);
      next_vblank = (next_vc < vbp || next_vc >= vbp + vvisible);
   end

   //
   // character generation
   //
   always @(posedge clk) begin
      if (reset) begin
         row <= 0;
         col <= 0;
         rowc <= 0;
         colc <= 0;
         char <= 0;
      end
      else begin
         row <= next_row;
         col <= next_col;
         rowc <= next_rowc;
         colc <= next_colc;
         char <= next_char;
      end
   end

   always @(*) begin
      if (vblank) begin
         next_row = 0;
         next_rowc = 0;
         next_col = 0;
         next_colc = 0;
         next_char = first_char;
      end
      // we need next_hblank here because we must detect the edge
      // in hblank & prepare for the row
      else if (next_hblank) begin
         // some nice defaults
         next_row = row;
         next_rowc = rowc;
         next_col = 0;
         next_colc = 0;
         next_char = char;

         // only do this once per line (positive hblank edge)
         if (hblank == 0) begin
            if (rowc == 15) begin
               // we are moving to the next row, so char
               // is already set at the correct value, unless
               // we reached the end of the buffer
               next_row = row + 1;
               next_rowc = 0;
               if (char == PAST_LAST_ROW) begin
                  next_char = 0;
               end
            end
            else begin
               // we are still on the same row, so
               // go back to the first char in this line
               next_char = char - COLS;
               next_rowc = rowc + 1;
            end
         end
      end
      else begin
         // some nice defaults
         next_row = row;
         next_rowc = rowc;
         next_col = col;
         next_colc = colc+1;
         next_char = char;

         if (colc == 7) begin
            // prepare to read next char (it takes two cycles,
            // one to read from ram & one to read from rom)
            // Since the memory bus runs at twice the pixel clock rate
            // we can do it just at the last pixel
            next_char = char+1;
            // move to the next char
            next_col = col+1;
            next_colc = 0;
         end
      end // else: !if(next_hblank)
   end // always @ (*)

   //
   // pixel out (char & cursor combination)
   //
   always @(posedge clk) begin
      if (reset) video <= video_off;
      else video <= combined_pixel;
   end

   always @(*) begin
      // cursor pixel: invert video when we are under the cursor (if it's blinking)
      is_under_cursor = (cursor_x == col) & (cursor_y == row);
      cursor_pixel = is_under_cursor & cursor_blink_on;
      // char pixel: read from the appropiate char, row & col on the font ROM,
      // the pixels LSB->MSB ordered
      char_pixel = char_rom_data[7 - colc];
      // combine, but only emit video on non-blanking periods
      combined_pixel = (next_hblank || next_vblank)?
                       video_off :
                       char_pixel ^ cursor_pixel;
   end
endmodule // video_generator