# Contributor: Aaron Laursen <aaronlaursen@gmail.com>

pkgname=STUFFS-git
_gitname=STUFFS
pkgver=0.0.0
pkgrel=1
pkgdesc="a Semantically-Tagged, Unorganized, Future File-System: STUFFS"
arch=('i686' 'x86_64')
url="https://github.com/aaronlaursen/STUFFS"
license=('custom:ISC')
depends=('python sqlite python-sqlalchemy python-fusepy-git')
makedepends=('git')
conflicts=()
provides=()
# The git repo is detected by the 'git:' or 'git+' bedginning. The branch
# 'pacman41' is then checked out upon cloning, expediating versioning:
#source=('git+https://github.com/falconindy/expac.git'
source=('git://github.com/aaronlaursen/${_gitname}.git')
# Because the sources are not static, skip Git checksum:
md5sums=('SKIP')

pkgver() {
  cd $_gitname
  # Use the tag of the last commit
  git describe --always | sed 's|-|.|g'
}

build() {
  cd $_gitname
  make
}

package() {
  cd $_gitname
  install -D "$srcdir/STUFFS.py" "$pkgdir/usr/bin/STUFFS.py"
  install -D "$srcdir/README.md" "$pkgdir/usr/share/STUFFS/README.md"
}
