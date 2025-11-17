<div bind:this={chartDiv} id="chart"></div>

<script lang="ts">
  import { createChart } from 'lightweight-charts';

  let chart: ReturnType<typeof createChart> | null = null;
  
  let chartDiv: HTMLDivElement | null = null;

  const chart = createChart(chartDiv)
</script>