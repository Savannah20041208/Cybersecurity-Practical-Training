<template>
  <div class="molecular-structure transition-transform duration-500 ease-in-out">
    <!-- 阿司匹林分子结构 -->
    <svg v-if="drugId === 'DRUG001' || drugName === '阿司匹林'" 
         width="300" height="250" viewBox="0 0 300 250" class="w-full h-full">
      <!-- 苯环 -->
      <g stroke="#333" stroke-width="2" fill="none">
        <!-- 苯环骨架 -->
        <polygon points="80,120 120,100 160,120 160,160 120,180 80,160" stroke="#333" fill="none"/>
        
        <!-- 羧基 (-COOH) -->
        <line x1="160" y1="120" x2="200" y2="110"/>
        <line x1="200" y1="110" x2="220" y2="120"/>
        <line x1="220" y1="120" x2="240" y2="110"/>
        <line x1="220" y1="120" x2="220" y2="140"/>
        <line x1="220" y1="140" x2="240" y2="150"/>
        
        <!-- 乙酰基 (-OCOCH3) -->
        <line x1="120" y1="100" x2="120" y2="70"/>
        <line x1="120" y1="70" x2="100" y2="60"/>
        <line x1="100" y1="60" x2="80" y2="70"/>
        <line x1="100" y1="60" x2="100" y2="40"/>
        <line x1="100" y1="40" x2="80" y2="30"/>
      </g>
      
      <!-- 原子标签 -->
      <g font-family="Arial, sans-serif" font-size="14" font-weight="bold">
        <!-- 碳原子 (通常不标注，但这里为了清晰显示) -->
        <circle cx="80" cy="120" r="8" fill="#333"/>
        <circle cx="120" cy="100" r="8" fill="#333"/>
        <circle cx="160" cy="120" r="8" fill="#333"/>
        <circle cx="160" cy="160" r="8" fill="#333"/>
        <circle cx="120" cy="180" r="8" fill="#333"/>
        <circle cx="80" cy="160" r="8" fill="#333"/>
        
        <!-- 氧原子 (红色) -->
        <circle cx="120" cy="70" r="8" fill="#ff0000"/>
        <text x="115" y="75" fill="white" font-size="10">O</text>
        
        <circle cx="100" cy="40" r="8" fill="#ff0000"/>
        <text x="95" y="45" fill="white" font-size="10">O</text>
        
        <circle cx="220" cy="120" r="8" fill="#ff0000"/>
        <text x="215" y="125" fill="white" font-size="10">O</text>
        
        <circle cx="240" cy="150" r="8" fill="#ff0000"/>
        <text x="235" y="155" fill="white" font-size="10">O</text>
        
        <!-- 氢原子 (白色) -->
        <circle cx="240" cy="110" r="6" fill="#ffffff" stroke="#333"/>
        <text x="237" y="114" fill="#333" font-size="8">H</text>
        
        <!-- 甲基 -->
        <circle cx="80" cy="30" r="8" fill="#333"/>
        <text x="70" y="25" fill="#333" font-size="10">CH₃</text>
      </g>
      
      <!-- 分子名称 -->
      <text x="150" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#333">
        阿司匹林 (Aspirin)
      </text>
      <text x="150" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#666">
        C₉H₈O₄
      </text>
    </svg>
    
    <!-- 恩替卡韦分子结构 -->
    <svg v-else-if="drugId === 'DRUG001' || drugName === '恩替卡韦'" 
         width="300" height="250" viewBox="0 0 300 250" class="w-full h-full">
      <!-- 嘌呤环系统 -->
      <g stroke="#333" stroke-width="2" fill="none">
        <!-- 六元环 -->
        <polygon points="100,100 140,80 180,100 180,140 140,160 100,140" stroke="#333" fill="none"/>
        <!-- 五元环 -->
        <polygon points="140,80 180,100 200,60 160,40 140,80" stroke="#333" fill="none"/>
        
        <!-- 糖环 -->
        <polygon points="80,140 60,180 100,200 140,180 120,140" stroke="#333" fill="none"/>
        
        <!-- 连接线 -->
        <line x1="100" y1="140" x2="80" y2="140"/>
        <line x1="200" y1="60" x2="220" y2="40"/>
        <line x1="60" y1="180" x2="40" y2="200"/>
      </g>
      
      <!-- 原子标签 -->
      <g font-family="Arial, sans-serif" font-size="12" font-weight="bold">
        <!-- 氮原子 (蓝色) -->
        <circle cx="140" cy="80" r="8" fill="#0000ff"/>
        <text x="137" y="84" fill="white" font-size="8">N</text>
        
        <circle cx="180" cy="100" r="8" fill="#0000ff"/>
        <text x="177" y="104" fill="white" font-size="8">N</text>
        
        <circle cx="200" cy="60" r="8" fill="#0000ff"/>
        <text x="197" y="64" fill="white" font-size="8">N</text>
        
        <!-- 氧原子 (红色) -->
        <circle cx="60" cy="180" r="8" fill="#ff0000"/>
        <text x="57" y="184" fill="white" font-size="8">O</text>
        
        <circle cx="40" cy="200" r="8" fill="#ff0000"/>
        <text x="37" y="204" fill="white" font-size="8">O</text>
        
        <!-- 氢原子 -->
        <circle cx="220" cy="40" r="6" fill="#ffffff" stroke="#333"/>
        <text x="217" y="44" fill="#333" font-size="8">H</text>
      </g>
      
      <!-- 分子名称 -->
      <text x="150" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#333">
        恩替卡韦 (Entecavir)
      </text>
      <text x="150" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#666">
        C₁₂H₁₅N₅O₃
      </text>
    </svg>
    
    <!-- 索拉非尼分子结构 -->
    <svg v-else-if="drugName === '索拉非尼'" 
         width="300" height="250" viewBox="0 0 300 250" class="w-full h-full">
      <!-- 复杂的多环结构 -->
      <g stroke="#333" stroke-width="2" fill="none">
        <!-- 吡啶环 -->
        <polygon points="60,100 100,80 140,100 140,140 100,160 60,140" stroke="#333" fill="none"/>
        
        <!-- 苯环 -->
        <polygon points="160,100 200,80 240,100 240,140 200,160 160,140" stroke="#333" fill="none"/>
        
        <!-- 连接基团 -->
        <line x1="140" y1="100" x2="160" y2="100"/>
        <line x1="200" y1="80" x2="220" y2="60"/>
        <line x1="240" y1="100" x2="260" y2="90"/>
        
        <!-- 三氟甲基 -->
        <line x1="260" y1="90" x2="280" y2="80"/>
      </g>
      
      <!-- 原子标签 -->
      <g font-family="Arial, sans-serif" font-size="12" font-weight="bold">
        <!-- 氮原子 -->
        <circle cx="100" cy="80" r="8" fill="#0000ff"/>
        <text x="97" y="84" fill="white" font-size="8">N</text>
        
        <circle cx="220" cy="60" r="8" fill="#0000ff"/>
        <text x="217" y="64" fill="white" font-size="8">N</text>
        
        <!-- 氧原子 -->
        <circle cx="260" cy="90" r="8" fill="#ff0000"/>
        <text x="257" y="94" fill="white" font-size="8">O</text>
        
        <!-- 氟原子 (浅绿色) -->
        <circle cx="280" cy="80" r="8" fill="#90EE90"/>
        <text x="277" y="84" fill="#333" font-size="8">F</text>
        
        <!-- 氯原子 (绿色) -->
        <circle cx="60" cy="100" r="8" fill="#00ff00"/>
        <text x="56" y="104" fill="#333" font-size="8">Cl</text>
      </g>
      
      <!-- 分子名称 -->
      <text x="150" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#333">
        索拉非尼 (Sorafenib)
      </text>
      <text x="150" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#666">
        C₂₁H₁₆ClF₃N₄O₃
      </text>
    </svg>
    
    <!-- 熊去氧胆酸分子结构 -->
    <svg v-else-if="drugName === '熊去氧胆酸'" 
         width="300" height="250" viewBox="0 0 300 250" class="w-full h-full">
      <!-- 甾体骨架 -->
      <g stroke="#333" stroke-width="2" fill="none">
        <!-- A环 -->
        <polygon points="60,120 90,100 120,120 120,150 90,170 60,150" stroke="#333" fill="none"/>
        <!-- B环 -->
        <polygon points="120,120 150,100 180,120 180,150 150,170 120,150" stroke="#333" fill="none"/>
        <!-- C环 -->
        <polygon points="180,120 210,100 240,120 240,150 210,170 180,150" stroke="#333" fill="none"/>
        <!-- D环 -->
        <polygon points="210,100 240,80 270,100 270,130 240,150 210,130" stroke="#333" fill="none"/>
        
        <!-- 侧链 -->
        <line x1="270" y1="100" x2="290" y2="90"/>
        <line x1="290" y1="90" x2="310" y2="100"/>
        
        <!-- 羟基 -->
        <line x1="90" y1="100" x2="90" y2="80"/>
        <line x1="150" y1="170" x2="150" y2="190"/>
        <line x1="240" y1="80" x2="240" y2="60"/>
      </g>
      
      <!-- 原子标签 -->
      <g font-family="Arial, sans-serif" font-size="12" font-weight="bold">
        <!-- 氧原子 -->
        <circle cx="90" cy="80" r="8" fill="#ff0000"/>
        <text x="87" y="84" fill="white" font-size="8">O</text>
        
        <circle cx="150" cy="190" r="8" fill="#ff0000"/>
        <text x="147" y="194" fill="white" font-size="8">O</text>
        
        <circle cx="240" cy="60" r="8" fill="#ff0000"/>
        <text x="237" y="64" fill="white" font-size="8">O</text>
        
        <circle cx="310" cy="100" r="8" fill="#ff0000"/>
        <text x="307" y="104" fill="white" font-size="8">O</text>
        
        <!-- 氢原子 -->
        <circle cx="85" cy="70" r="6" fill="#ffffff" stroke="#333"/>
        <text x="82" y="74" fill="#333" font-size="8">H</text>
        
        <circle cx="155" cy="200" r="6" fill="#ffffff" stroke="#333"/>
        <text x="152" y="204" fill="#333" font-size="8">H</text>
      </g>
      
      <!-- 分子名称 -->
      <text x="150" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#333">
        熊去氧胆酸 (UDCA)
      </text>
      <text x="150" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#666">
        C₂₄H₄₀O₄
      </text>
    </svg>
    
    <!-- 默认通用分子结构 -->
    <svg v-else width="300" height="250" viewBox="0 0 300 250" class="w-full h-full">
      <!-- 通用有机分子结构 -->
      <g stroke="#333" stroke-width="2" fill="none">
        <!-- 中心苯环 -->
        <polygon points="120,100 160,80 200,100 200,140 160,160 120,140" stroke="#333" fill="none"/>
        
        <!-- 侧链1 -->
        <line x1="120" y1="100" x2="80" y2="90"/>
        <line x1="80" y1="90" x2="60" y2="100"/>
        
        <!-- 侧链2 -->
        <line x1="200" y1="100" x2="240" y2="90"/>
        <line x1="240" y1="90" x2="260" y2="100"/>
        
        <!-- 官能团 -->
        <line x1="160" y1="80" x2="160" y2="50"/>
        <line x1="160" y1="160" x2="160" y2="190"/>
      </g>
      
      <!-- 原子标签 -->
      <g font-family="Arial, sans-serif" font-size="12" font-weight="bold">
        <!-- 碳原子 -->
        <circle cx="120" cy="100" r="8" fill="#333"/>
        <circle cx="160" cy="80" r="8" fill="#333"/>
        <circle cx="200" cy="100" r="8" fill="#333"/>
        <circle cx="160" cy="160" r="8" fill="#333"/>
        
        <!-- 氧原子 -->
        <circle cx="160" cy="50" r="8" fill="#ff0000"/>
        <text x="157" y="54" fill="white" font-size="8">O</text>
        
        <circle cx="160" cy="190" r="8" fill="#ff0000"/>
        <text x="157" y="194" fill="white" font-size="8">O</text>
        
        <!-- 其他原子 -->
        <circle cx="60" cy="100" r="8" fill="#0000ff"/>
        <text x="57" y="104" fill="white" font-size="8">N</text>
        
        <circle cx="260" cy="100" r="8" fill="#ffff00"/>
        <text x="257" y="104" fill="#333" font-size="8">S</text>
      </g>
      
      <!-- 分子名称 -->
      <text x="150" y="220" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#333">
        {{ drugName || '药物分子' }}
      </text>
      <text x="150" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#666">
        分子结构图
      </text>
    </svg>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  drugId: {
    type: String,
    default: ''
  },
  drugName: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.molecular-structure {
  transition: transform 0.5s ease-in-out;
}

.molecular-structure:hover {
  transform: scale(1.05);
}

/* 原子颜色标准 */
/* 碳: #333333 (黑色) */
/* 氧: #ff0000 (红色) */
/* 氮: #0000ff (蓝色) */
/* 氢: #ffffff (白色) */
/* 硫: #ffff00 (黄色) */
/* 磷: #ff8c00 (橙色) */
/* 氯: #00ff00 (绿色) */
/* 氟: #90EE90 (浅绿色) */
</style>






