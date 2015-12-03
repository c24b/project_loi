// moissonneur-republique-numerique -- Harvest https://www.republique-numerique.fr/
// By: Emmanuel Raviart <emmanuel.raviart@data.gouv.fr>
//
// Copyright (C) 2015 Etalab
// https://git.framasoft.org/etalab/moissonneur-republique-numerique
//
// moissonneur-republique-numerique is free software; you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// moissonneur-republique-numerique is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


import assert from "assert"
import fetch from "node-fetch"
import fs from "mz/fs"
import mkdirp from "mkdirp"
import path from "path"
import url from "url"


const baseUrl = "https://www.republique-numerique.fr/"
const binaryExtensions = [".eot", ".jpg", ".png", ".ttf", ".woff", ".woff2"]
let pathsFetched = []
let pathsToFetch = [
  "/",
  "/api/categories",
  "/api/features",
  "/get_api_token",
]


function addPageToFetch(pagePath) {
  if (pagePath.startsWith("/") && !pagePath.startsWith("//") && !pathsFetched.includes(pagePath) &&
      !pathsToFetch.includes(pagePath)) {
    pathsToFetch.push(pagePath)
  }
}

async function main() {
  const siteDir = process.argv[2]
  assert(siteDir, "Argument manquant pour le chemin où stocker le site")
  if (!await fs.exists(siteDir)) await fs.mkdir(siteDir)

  let translations = {}
  while (pathsToFetch.length > 0) {
    let pathToFetch = pathsToFetch.shift()
    let pagePath = pathToFetch.split("?")[0]
    pagePath = path.join(siteDir, pagePath.endsWith("/") ? path.join(pagePath, "index.html") : pagePath)
    let splitPagePath = pagePath.split("/")
    let pageName = splitPagePath[splitPagePath.length - 1]
    if (pageName.length > 250) {
      let translatedPageName = pageName.substring(0, 250)
      splitPagePath[splitPagePath.length - 1] = translatedPageName
      let translatedPagePath = splitPagePath.join("/")
      translations[pagePath] = translatedPagePath
      pagePath = translatedPagePath
      let translationsFile = await fs.open(path.join(siteDir, `translations.json`), "w")
      await fs.write(translationsFile, JSON.stringify(translations, null, 2))
      fs.close(translationsFile)
    }
    let extension = path.extname(pagePath)
    if (!extension) {
      extension = pathToFetch === "/get_api_token" || pathToFetch.startsWith("/api/") ? ".json" : ".html"
      pagePath += extension
    }

    mkdirp.sync(path.dirname(pagePath))
    let page
    if (await fs.exists(pagePath)) {
      // console.log(`Reading URL ${pathToFetch} from ${pagePath}.`)
      page = await fs.readFile(pagePath, {encoding: "utf-8"})
    } else {
      console.log(`Fetching URL ${pathToFetch}.`)
      let res = await fetch(url.resolve(baseUrl, pathToFetch))
      page = await res.text()
      console.log(`Writing page ${pagePath}.`)

      let pageFile = await fs.open(pagePath, "w")
      if (binaryExtensions.includes(extension)) {
        let buffer = Buffer.concat(res._raw)
        await fs.write(pageFile, buffer, 0, buffer.length)
      } else {
        await fs.write(pageFile, page)
      }
      fs.close(pageFile)
    }
    pathsFetched.push(pathToFetch)

    let match
    if (extension === ".css") {
      let urlRe = /url\(\.\.(.*?)\)/g
      while ((match = urlRe.exec(page)) !== null) {
        let srcPath = match[1].split("#")[0]
        addPageToFetch(srcPath)
      }
    } else if (extension === ".html") {
      let urlRe = /(content|href|src)="(.*?)"/g
      while ((match = urlRe.exec(page)) !== null) {
        let srcPath = match[2].split("#")[0]
        addPageToFetch(srcPath)
      }

      let dataOpinionRe = /data-opinion="(.*?)"/g
      while ((match = dataOpinionRe.exec(page)) !== null) {
        let opinionNumber = match[1]
        addPageToFetch(`/api/opinions/${opinionNumber}`)
        addPageToFetch(`/api/opinions/${opinionNumber}/sources?offset=0&limit=50&filter=last`)
        addPageToFetch(`/api/opinions/${opinionNumber}/versions?offset=0&filter=last`)
      }
    } else if (extension === ".json") {
      if (pageName === "versions") {
        let versionsData = JSON.parse(page)
        for (let version of versionsData.versions) {
          addPageToFetch(`${pathToFetch.split("?")[0]}/${version.id}`)
        }
      }
    }
  }
}


main()
  .catch(error => console.log(error.stack))
