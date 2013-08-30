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
source=('git://github.com/aaronlaursen/STUFFS.git')
md5sums=('SKIP')

pkgver() {
  cd $_gitname
  # Use the tag of the last commit
  git describe --always | sed 's|-|.|g'
}

build() {
}

package() {
  cd $_gitname
  install -D "$srcdir/STUFFS.py" "$pkgdir/usr/bin/STUFFS.py"
  install -D "$srcdir/README.md" "$pkgdir/usr/share/STUFFS/README.md"
}
