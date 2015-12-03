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
import path from "path"
import url from "url"


const baseUrl = "https://www.republique-numerique.fr/api/"


async function main() {
  const opinionsDir = process.argv[2]
  assert(opinionsDir, "Argument manquant pour le chemin où stocker les opinions")
  if (!await fs.exists(opinionsDir)) await fs.mkdir(opinionsDir)

  let consecutive404Count = 0
  let opinionNumber = 0
  while (consecutive404Count < 100) {
    console.log(`Récupération de l'opinion ${opinionNumber}`)
    let res = await fetch(url.resolve(baseUrl, `opinions/${opinionNumber}`))
    let data = await res.json()
    if (data.code) {
      assert.equal(data.code, 404, data)
      consecutive404Count += 1
      console.log(`  Opinion absente (${consecutive404Count} consécutives)`)
    } else {
      consecutive404Count = 0
      let opinionDir = path.join(opinionsDir, `opinion-${opinionNumber}`)
      if (!await fs.exists(opinionDir)) await fs.mkdir(opinionDir)
      let outputFile = await fs.open(path.join(opinionDir, `opinion.json`), "w")
      await fs.write(outputFile, JSON.stringify(data, null, 2))
      fs.close(outputFile)

      console.log(`  Récupération de la liste des versions de l'opinion`)
      let versionsRes = await fetch(url.resolve(baseUrl, `opinions/${opinionNumber}/versions`))
      let versionsData = await versionsRes.json()
      assert(!versionsData.code, data)
      for (let version of versionsData.versions) {
        console.log(`  Récupération de la version ${version.id} de l'opinion`)
        let versionRes = await fetch(url.resolve(baseUrl, `opinions/${opinionNumber}/versions/${version.id}`))
        let versionData = await versionRes.json()
        assert(!versionData.code, data)
        outputFile = await fs.open(path.join(opinionDir, `version-${version.id}.json`), "w")
        await fs.write(outputFile, JSON.stringify(versionData, null, 2))
        fs.close(outputFile)
      }
    }
    opinionNumber += 1
  }
}


main()
  .catch(error => console.log(error.stack))
