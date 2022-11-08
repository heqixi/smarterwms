<template>
  <q-page class="flex flex-top content-start">
    <template>
      <div class="q-pa-md">
        <div class="q-gutter-y-md" style="max-width: 100%">
          <q-tabs v-model="detaillink">
            <transition appear enter-active-class="animated zoomIn">
              <q-route-tab name="fetchlist" :label="$t('fetch.fetchlist')" icon="collections" :to="{ name: 'fetchlist' }" exact/>
            </transition>
            <transition appear enter-active-class="animated zoomIn">
              <q-route-tab name="arealist" :label="$t('fetch.arealist')" icon="place" :to="{ name: 'arealist' }" exact/>
            </transition>
          </q-tabs>
        </div>
      </div>
    </template>
    <div class="main-table">
      <router-view />
    </div>
  </q-page>
</template>

<script>
export default {
  name: 'FetchBox',
  data () {
    return {
      detaillink: 'fetchlist'
    }
  },
  methods: {
  }
}
</script>
