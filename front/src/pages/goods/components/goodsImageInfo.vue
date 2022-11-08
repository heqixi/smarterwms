<template>
  <q-card>
    <q-banner inline-actions class="text-white bg-blue-5">图片信息</q-banner>
    <q-card-section>
      <div>
        <div class="row q-mb-sm">
          <div class="text-body2">
            采集图片库
          </div>
        </div>
        <div class="q-mt-sm row items-start">
          <q-img
            draggable="true"
            @dragstart="onDragStart"
            v-for="(image, index) in imageOptions"
            :id="'option-' + image.id"
            :key="index"
            :src="image.url"
            style="width: 150px"
            ratio="1"
            spinner-color="white"
            class="rounded-borders q-mr-sm q-mt-sm">
          </q-img>
        </div>

        <div class="row q-mt-lg">
          <span  :style="{color:'red', fontSize:'8px'}"> * </span>
          <div class="text-body2">
            商品图片
          </div>
        </div>
        <div class="row q-mt-md"
             @dragenter="onDragEnter"
             @dragleave="onDragLeave"
             @dragover="onDragOver"
             @drop="onDrop">
          <div v-for="(image, index) in images" :key=index class="col-1.5 q-mr-sm" >
            <q-card
              :id="index"
              class="image-card q-mb-sm">
              <q-img
                :id = 'image.imageId'
                draggable="true"
                @dragstart="onImageDragStart"
                v-if="image.url"
                :src="image.url"
                style="width: 150px"
                ratio="1"
                spinner-color="white"
                class="rounded-borders">
                <q-icon class="absolute all-pointer-events"
                        dense
                        size="32px" name="clear" color="red" style="top: 8px; right: 8px"
                        @click="deleteImge(index)">
                  <q-tooltip>
                    删除
                  </q-tooltip>
                </q-icon>
              </q-img>
              <div v-else class="row" :style="{height: '150px', width:'150px'}">
                <q-btn class="col-12" flat @click="choseImage()">选择采集图片</q-btn>
                <q-btn class="col-12" flat @click="uploadImage()">本地上传</q-btn>
                <q-btn class="col-12" flat>图片链接</q-btn>
              </div>
            </q-card>
          </div>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>
import UploadImageDialog from 'pages/goods/components/uploadImageDialog'

export default {
  name: 'GoodsBaseInfo',
  data () {
    return {
      // images: [
      //   {
      //     url: undefined,
      //     label: 'test',
      //     media: undefined,
      //     imageId: 'image-' + 0
      //   },
      //   {
      //     url: undefined,
      //     label: 'test',
      //     media: undefined,
      //     imageId: 'image-' + 1
      //   },
      //   {
      //     url: undefined,
      //     label: 'test',
      //     media: undefined,
      //     imageId: 'image-' + 2
      //   },
      //   {
      //     url: undefined,
      //     label: 'test',
      //     media: undefined,
      //     imageId: 'image-' + 3
      //   },
      //   {
      //     url: undefined,
      //     label: 'test',
      //     media: undefined,
      //     imageId: 'image-' + 4
      //   },
      //   {
      //     url: undefined,
      //     label: 'test',
      //     media: undefined,
      //     imageId: 'image-' + 5
      //   },
      //   {
      //     url: undefined,
      //     label: 'test',
      //     media: undefined,
      //     imageId: 'image-' + 6
      //   },
      //   {
      //     url: undefined,
      //     label: 'test',
      //     media: undefined,
      //     imageId: 'image-' + 7
      //   }
      // ],
      baseInfo: {
        goods_name: '',
        goods_code: '',
        goods_desc: '',
        goods_class: '',
        goods_media: []
      },
      media_saved: new Map(),
      meida_form_fields: [],
      error1: this.$t('goods.view_goodslist.error1'),
      status1: [],
      status2: []
    }
  },
  methods: {
    choseImage () {
      this.$q.notify({
        message: '请直接拖拽图片到你想要的位置',
        icon: 'check',
        color: 'green'
      })
    },
    uploadImage () {
      var _this = this
      _this.$q.dialog({
        component: UploadImageDialog,
        uploadPathName: _this.uploadPathName
      }).onOk((imagesInfos) => {
        console.log('upload image ok', imagesInfos)
        _this.fillImages(imagesInfos)
      })
    },
    fillImages (imagesInfos) {
      var _this = this
      imagesInfos.forEach(imageInfo => {
        for (let i = 0; i < _this.images.length; i++) {
          if (_this.images[i].url === undefined) {
            _this.images[i].url = imageInfo.url
            _this.images[i].media = imageInfo.id
            break
          }
        }
      })
      _this.saveImages()
    },
    deleteImge (index) {
      this.images[index].url = undefined
      this.saveImages()
    },

    onDragStart (e) {
      e.dataTransfer.setData('optionImageId', e.target.id)
      e.dataTransfer.dropEffect = 'move'
    },

    onImageDragStart (e) {
      e.dataTransfer.setData('imageId', e.target.id)
      e.dataTransfer.dropEffect = 'move'
    },
    onDragEnter (e) {
      // don't drop on other draggables
      // console.log('on drags enter ', e)
      if (e.target.draggable !== true) {
        e.target.classList.add('drag-enter')
      }
    },

    onDragLeave (e) {
      e.target.classList.remove('drag-enter')
    },

    onDragOver (e) {
      // console.log('on drags over ', e)
      e.preventDefault()
    },

    onDrop (e) {
      e.preventDefault()
      // don't drop on other draggables
      if (e.target.draggable === true) {
        return
      }
      const optionImageEleId = e.dataTransfer.getData('optionImageId')
      const imageId = e.dataTransfer.getData('imageId')
      const elementId = optionImageEleId || imageId
      const draggedEl = document.getElementById(elementId)
      // check if original parent node
      if (draggedEl.parentNode === e.target) {
        e.target.classList.remove('drag-enter')
        return
      }
      const cardId = this.findTargetImageIndex(e.target, 0, 10)
      if (imageId) {
        this.exchangeImagePosition(imageId, 'image-' + cardId)
      } else if (optionImageEleId) {
        this.addDragImage(cardId, optionImageEleId.split('-')[1])
      }
      e.target.classList.remove('drag-enter')
    },
    exchangeImagePosition (from, to) {
      let fromIndex = 0
      let toIndex = 0
      for (var i = 0; i < this.images.length; i++) {
        if (this.images[i].imageId === from) {
          fromIndex = i
        }
        if (this.images[i].imageId === to) {
          toIndex = i
        }
      }
      const toImage = this.images[toIndex]
      const fromImage = this.images.splice(fromIndex, 1, toImage)[0]
      const toImageId = toImage.imageId
      toImage.imageId = fromImage.imageId
      fromImage.imageId = toImageId
      this.images.splice(toIndex, 1, fromImage)
      this.saveImages()
    },
    findTargetImageIndex (htmlEl, depth, maxDepth) {
      if (depth > maxDepth) {
        console.log('target html not found')
        return ''
      }
      const outerHTML = htmlEl.outerHTML
      if (outerHTML.indexOf('image-card') > 0) {
        return htmlEl.id
      }
      return this.findTargetImageIndex(htmlEl.parentNode, depth + 1, 10)
    },
    addDragImage (cardId, imageOptionId) {
      console.log('add dray image ', cardId, imageOptionId)
      const image = this.images[cardId]
      const imageOption = this.imageOptions.find(image => { return (image.id + '') === imageOptionId })
      image.url = imageOption.url
      image.update = true
      this.saveImages()
    },
    mediaFileUploadFactory (files) {
      const formFieldsWithTags = []
      files.forEach(file => {
        formFieldsWithTags.push({
          name: file.name,
          value: 'V'
        })
      })
      return {
        formFields: formFieldsWithTags
      }
    },
    saveImages () {
      this.$emit('onChange', this.images)
    },
    newDataSubmit () {
      console.log('new base info summit')
      this.$emit('baseInfoSummit', this.baseInfo)
    },
    onRejected (rejectedEntries) {
      // Notify plugin needs to be installed
      // https://quasar.dev/quasar-plugins/notify#Installation
      console.log('upload file on reject')
      this.$q.notify({
        type: 'negative',
        message: `${rejectedEntries.length} file(s) did not pass validation constraints`
      })
    },
    onFileUploaded (info) {
      console.log('media file uploaded, info', info)
      var _this = this
      const response = info.xhr.response
      const data = JSON.parse(response)
      data.forEach(uploadImage => {
        for (let i = 0; i < _this.images.length; i++) {
          if (!_this.images[i].url) {
            _this.images[i].url = uploadImage.url
            _this.images[i].media = uploadImage.id
            break
          }
        }
      })
      this.newDataSubmit()
    },
    onFileAdded (files) {
      console.log('file added ', files)
      files.forEach(file => {
        if (file.type.indexOf('video') !== -1) {
          this.meida_form_fields.push({
            name: file.name,
            value: 'Video'
          })
        } else {
          this.meida_form_fields.push({
            name: file.name,
            value: 'DescImage'
          })
        }
      })
    },
    onFileRemoved (files) {
      console.log('onFile removed ', files)
    }
  },
  computed: {
    images () {
      const _images = this.data.map((image, index) => {
        return {
          url: image.url,
          label: 'test',
          media: undefined,
          imageId: 'image-' + index
        }
      })
      if (_images.length < 8) {
        for (let i = _images.length; i < 8; i++) {
          _images.push(
            {
              url: undefined,
              label: 'test',
              media: undefined,
              imageId: 'image-' + i
            }
          )
        }
      }
      return _images
    }
  },
  props: ['data', 'imageOptions', 'uploadPathName'],
  comments: {
    UploadImageDialog
  }
}
</script>
