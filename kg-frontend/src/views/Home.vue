<template>
  <div class="flex flex-col items-center justify-center p-4 md:p-8 min-h-[calc(100vh-200px)]">
    <div class="w-full max-w-6xl mx-auto">
      <!-- 标题区域 -->
      <div class="text-center mb-8 md:mb-12 relative">
        <div class="absolute -top-6 left-1/2 transform -translate-x-1/2 w-24 h-1 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full"></div>
        <h2 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold text-gray-800 mb-3 relative inline-block">
          智慧医疗知识问答
          <span class="absolute -bottom-2 left-0 w-full h-1 bg-gradient-to-r from-blue-400 to-transparent rounded-full"></span>
        </h2>
        <p class="text-gray-600 max-w-2xl mx-auto mt-4">
          基于知识图谱的智慧医疗知识服务平台，为您提供专业的医疗健康咨询、疾病诊断建议和治疗方案推荐
        </p>

        <!-- 功能标签 -->
        <div class="flex flex-wrap justify-center gap-2 mt-6">
          <span class="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full">疾病诊断</span>
          <span class="bg-indigo-100 text-indigo-800 text-xs px-3 py-1 rounded-full">症状分析</span>
          <span class="bg-purple-100 text-purple-800 text-xs px-3 py-1 rounded-full">药物咨询</span>
          <span class="bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full">健康建议</span>
        </div>
      </div>

      <ChatBox />
    </div>
  </div>
</template>

<script setup>
import ChatBox from '../components/ChatBox.vue'
</script>

<style>
body {
  font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
  scroll-behavior: smooth;
}
</style>
