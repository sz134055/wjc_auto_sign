<template>
    <div class="footer-box">
        <div class="info-box">
            <div class="title-large-box">
                <span class="global-title-large">Auto</span>
                <span class="global-title-large">Check-In</span>
            </div>
        </div>
        <div class="repo-box">
            <RepoBtn
                repo-url="https://github.com/sz134055/wjc_auto_sign"
                logo="https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png"
                description="Github"
             />
        </div>
       
    </div>
</template>

<script setup>
import RepoBtn from './RepoBtn.vue';
</script>

<style scoped>
.footer-box{
    width: 100%;
    height: fit-content;
    background-color: #1F2833;

    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 50px;
    align-items: center;
    flex-wrap: wrap;
}
.title-large-box {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap:10px;
}
.repo-box{
    display: flex;
    flex-direction: column;
    gap: 3px;
}
</style>