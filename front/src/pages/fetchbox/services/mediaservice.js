class MediaService {
  imgUrlToFile (url) {
    return new Promise(resolve => {
      const tempImage = new Image();
      // 如果图片url是网络url，要加下一句代码
      tempImage.crossOrigin = '*';
      tempImage.onload = () => {
        const base64 = this.getBase64Image(tempImage);
        const imgBlob = this.base64toBlob(base64);
        const filename = this.getFileName(url);
        const coverFile = this.blobToFile(imgBlob, filename);
        resolve({
          filename: filename,
          blob: coverFile,
          fileBytes: base64.split('base64,')[1]
        });
      };
      tempImage.src = url;
    });
  }

  getBase64Image (img) {
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, img.width, img.height);
    let ext = img.src.substring(img.src.lastIndexOf('.') + 1).toLowerCase();
    if (ext === 'jpg') {
      ext = 'jpeg';
    }
    return canvas.toDataURL('image/' + ext);
  }

  base64toBlob (base64) {
    const arr = base64.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], { type: mime });
  }

  blobToFile (blob, filename) {
    // edge浏览器不支持new File对象，所以用以下方法兼容
    blob.lastModifiedDate = new Date();
    blob.name = filename;
    return blob;
  }

  getFileName (url) {
    // 获取到文件名
    const pos = url.lastIndexOf('/'); // 查找最后一个/的位置
    return url.substring(pos + 1); // 截取最后一个/位置到字符长度，也就是截取文件名
  }
}

const mediaService = new MediaService();

export default mediaService;
